from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import CreateProjectResponse
from app.storage.paths import StoragePaths

router = APIRouter()


@router.post("/projects", response_model=CreateProjectResponse)
async def create_project(
    file: UploadFile = File(...),
) -> CreateProjectResponse:
    """Create a project by uploading an audio file."""
    storage = StoragePaths(data_dir="data")
    storage.ensure_base_dirs()

    project_id = str(uuid.uuid4())
    project = storage.project(project_id)
    project.base_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix == "":
        raise HTTPException(status_code=400, detail="File must have an extension")

    dst = project.input_file.with_suffix(suffix)
    await _save_upload(file, dst)

    project.input_file.unlink(missing_ok=True)
    dst.rename(project.input_file)

    return CreateProjectResponse(project_id=project_id)


async def _save_upload(file: UploadFile, dst: Path) -> None:
    """Save an UploadFile to disk."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    dst.write_bytes(content)
