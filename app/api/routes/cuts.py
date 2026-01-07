from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.schemas import ExportRequest, ExportResponse
from app.services.audio.cutter import AudioCutterService, ProjectMetadataStore
from app.services.audio.ffmpeg import AudioEncoder, FfmpegRunner
from app.storage.paths import StoragePaths

router = APIRouter()


@router.post("/projects/{project_id}/export", response_model=ExportResponse)
def export_segments(project_id: str, req: ExportRequest) -> ExportResponse:
    """Export MP3 files from provided segments."""
    storage = StoragePaths(data_dir=settings.data_dir)
    project = storage.project(project_id)

    if not project.base_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    service = AudioCutterService(
        encoder=AudioEncoder(runner=FfmpegRunner()),
        metadata_store=ProjectMetadataStore(),
    )

    try:
        return service.export(project, req)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
