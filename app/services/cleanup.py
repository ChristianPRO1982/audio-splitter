from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CleanupService:
    """Handle cleanup of stored data."""

    projects_root: Path

    def delete_project(self, project_id: str) -> None:
        """Delete a single project directory."""
        path = self.projects_root / project_id
        if path.exists():
            shutil.rmtree(path)

    def delete_all_projects(self) -> None:
        """Delete all projects."""
        if not self.projects_root.exists():
            return

        for item in self.projects_root.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
