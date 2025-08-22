from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


# Project schemas
class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    name: str
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    uid: Optional[str] = None
    name: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None


class ProjectCounts(BaseModel):
    shots: int
    tasks: int


class ProjectOverviewOut(BaseModel):
    uid: str
    name: str
    counts: ProjectCounts
    created_at: datetime


# Asset schemas
class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    name: str
    type: Optional[str]
    created_at: datetime
    updated_at: datetime


class AssetCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    name: str
    type: Optional[str] = None


class AssetUpdate(BaseModel):
    project_uid: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None


# Shot schemas
class ShotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    seq: str
    shot: str
    frame_in: int
    frame_out: int
    fps: Optional[float] = None
    colorspace: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ShotCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: Optional[str] = None
    project_uid: str
    seq: str
    shot: str
    frame_in: int
    frame_out: int
    fps: Optional[float] = None
    colorspace: Optional[str] = None


class ShotUpdate(BaseModel):
    project_uid: Optional[str] = None
    seq: Optional[str] = None
    shot: Optional[str] = None
    frame_in: Optional[int] = None
    frame_out: Optional[int] = None
    fps: Optional[float] = None
    colorspace: Optional[str] = None


# Task schemas
class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    parent_type: str
    parent_uid: Optional[str] = None
    name: str
    assignee: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


# Version schemas
class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    task_uid: Optional[str] = None
    vnum: int
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Publish schemas
class PublishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    version_uid: Optional[str] = None
    type: Optional[str] = None
    representation: Optional[str] = None
    path: str
    meta: dict
    created_at: datetime
    updated_at: datetime


# RenderJob schemas
class RenderJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    context: Dict[str, Any]
    adapter: str
    status: str
    logs: Optional[str] = None
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime


# Event schemas
class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    kind: str
    payload: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
