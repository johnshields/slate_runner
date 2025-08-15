from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ShotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    seq: str
    shot: str
    frame_in: int
    frame_out: int
    fps: Optional[float] = None
    colorspace: Optional[str] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    parent_type: str
    parent_id: int
    name: str
    assignee: Optional[str] = None
    status: str


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_id: int
    vnum: int
    status: str
    created_by: Optional[str] = None
    created_at: Optional[str] = None


class PublishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    version_id: int
    type: str
    representation: Optional[str] = None
    path: str
    meta: dict
    created_at: Optional[str] = None
