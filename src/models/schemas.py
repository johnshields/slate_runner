from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    name: str


class ProjectCounts(BaseModel):
    shots: int
    tasks: int


class ProjectOverviewOut(BaseModel):
    uid: str
    name: str
    counts: ProjectCounts


class ShotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_id: str
    seq: str
    shot: str
    frame_in: int
    frame_out: int
    fps: Optional[float] = None
    colorspace: Optional[str] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    parent_type: str
    parent_id: str
    name: str
    assignee: Optional[str] = None
    status: str


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    task_id: str
    vnum: int
    status: str
    created_by: Optional[str] = None
    created_at: Optional[str] = None


class PublishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    version_id: str
    type: str
    representation: Optional[str] = None
    path: str
    meta: dict
    created_at: Optional[str] = None
