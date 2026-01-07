from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True)
class ProjectPaths:
    """Compute and expose paths for a single project."""

    base_dir: Path

    @property
    def input_file(self) -> Path:
        return self.base_dir / "input"

    @property
    def metadata_file(self) -> Path:
        return self.base_dir / "metadata.json"

    @property
    def outputs_dir(self) -> Path:
        return self.base_dir / "outputs"


class StoragePaths:
    """Compute and manage application storage paths."""

    PROJECTS_DIR_NAME: Final[str] = "projects"
    UPLOADS_DIR_NAME: Final[str] = "uploads"
    OUTPUTS_DIR_NAME: Final[str] = "outputs"

    def __init__(self, data_dir: str) -> None:
        """Initialize storage root."""
        self._root = Path(data_dir)

    @property
    def root(self) -> Path:
        return self._root

    @property
    def projects_root(self) -> Path:
        return self._root / self.PROJECTS_DIR_NAME

    def project(self, project_id: str) -> ProjectPaths:
        return ProjectPaths(base_dir=self.projects_root / project_id)

    def ensure_base_dirs(self) -> None:
        """Create base dirs if missing."""
        self.projects_root.mkdir(parents=True, exist_ok=True)
