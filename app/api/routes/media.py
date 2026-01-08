from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.storage.paths import StoragePaths

router = APIRouter()


@router.get("/projects/{project_id}/audio")
def get_audio(project_id: str) -> FileResponse:
    """Serve the original audio file for a project."""
    storage = StoragePaths(data_dir="data")
    project = storage.project(project_id)
    if not project.input_file.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(path=str(project.input_file), filename=project.input_file.name)
