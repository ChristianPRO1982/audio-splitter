from __future__ import annotations

from pydantic import BaseModel, Field


class CreateProjectResponse(BaseModel):
    project_id: str


class Segment(BaseModel):
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    filename: str = Field(min_length=1, max_length=200)


class ExportRequest(BaseModel):
    segments: list[Segment]
    bitrate_kbps: int = Field(default=192, ge=64, le=320)


class ExportResultItem(BaseModel):
    filename: str
    output_path: str


class ExportResponse(BaseModel):
    items: list[ExportResultItem]
