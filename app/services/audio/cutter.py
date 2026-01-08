from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.models.schemas import ExportRequest, ExportResponse, ExportResultItem
from app.services.audio.ffmpeg import AudioEncoder
from app.storage.paths import ProjectPaths


@dataclass(frozen=True)
class ProjectMetadataStore:
    """Read and write project metadata."""

    def read(self, path: Path) -> dict[str, Any]:
        """Load metadata JSON if present, otherwise return empty."""
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, path: Path, payload: dict[str, Any]) -> None:
        """Write metadata JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@dataclass(frozen=True)
class AudioCutterService:
    """Export MP3 segments from a project input file."""

    encoder: AudioEncoder
    metadata_store: ProjectMetadataStore

    def export(self, project: ProjectPaths, req: ExportRequest) -> ExportResponse:
        """Export segments to the project's outputs directory."""
        project.outputs_dir.mkdir(parents=True, exist_ok=True)
        src = self._resolve_input(project)
        items = [self._export_one(project, src, seg, req.bitrate_kbps)
                 for seg in req.segments]
        self._persist_export(project, req)
        return ExportResponse(items=items)

    def _resolve_input(self, project: ProjectPaths) -> Path:
        """Locate the input file for a project."""
        if project.input_file.exists():
            return project.input_file
        raise FileNotFoundError("Project input file not found")

    def _export_one(self, project: ProjectPaths, src: Path, seg: Any,
                    bitrate_kbps: int) -> ExportResultItem:
        """Export a single segment."""
        safe_name = self._sanitize_filename(seg.filename)
        dst = project.outputs_dir / safe_name
        self.encoder.cut_to_mp3(src=src, start_s=seg.start_s, end_s=seg.end_s,
                                dst=dst, bitrate_kbps=bitrate_kbps)
        return ExportResultItem(filename=safe_name, output_path=str(dst))

    def _persist_export(self, project: ProjectPaths, req: ExportRequest) -> None:
        """Store export request in metadata."""
        meta = self.metadata_store.read(project.metadata_file)
        meta["last_export"] = req.model_dump()
        self.metadata_store.write(project.metadata_file, meta)

    def _sanitize_filename(self, filename: str) -> str:
        """Ensure filename is a simple mp3 name."""
        cleaned = filename.strip().replace("/", "_").replace("\\", "_")
        if not cleaned.lower().endswith(".mp3"):
            cleaned = f"{cleaned}.mp3"
        return cleaned
