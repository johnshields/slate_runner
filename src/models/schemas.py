from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


# Project schemas
class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    name: str
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    uid: Optional[str] = Field(None, min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100, description="Project name")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        # Remove extra whitespace
        return v.strip()

    @field_validator('uid')
    def validate_uid(cls, v):
        if v is not None:
            # UID should match pattern: PREFIX_XXXXXX
            if not re.match(r'^[A-Z]+_[A-Z0-9]{6}$', v):
                raise ValueError('UID must match pattern: PREFIX_XXXXXX (e.g., PROJ_ABC123)')
        return v


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
    uid: Optional[str] = Field(None, min_length=1, max_length=50)
    project_uid: str = Field(..., min_length=1, max_length=50)
    seq: str = Field(..., min_length=1, max_length=20, description="Sequence identifier")
    shot: str = Field(..., min_length=1, max_length=20, description="Shot identifier")
    frame_in: int = Field(..., ge=0, description="Start frame number")
    frame_out: int = Field(..., ge=0, description="End frame number")
    fps: Optional[float] = Field(None, ge=1.0, le=120.0, description="Frames per second")
    colorspace: Optional[str] = Field(None, max_length=50, description="Color space")

    @field_validator('frame_out')
    def validate_frame_range(cls, v, values):
        if 'frame_in' in values and v <= values['frame_in']:
            raise ValueError('frame_out must be greater than frame_in')
        return v

    @field_validator('seq', 'shot')
    def validate_identifiers(cls, v):
        if not re.match(r'^[A-Z0-9_]+$', v):
            raise ValueError(
                'Sequence and shot identifiers must contain only uppercase letters, numbers, and underscores')
        return v


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


class TaskCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    parent_type: Optional[Literal["asset", "shot"]] = None
    parent_uid: Optional[str] = None
    name: str
    assignee: Optional[str] = None
    status: Optional[str] = "WIP"


class TaskUpdate(BaseModel):
    project_uid: Optional[str] = None
    parent_type: Optional[Literal["asset", "shot"]] = None
    parent_uid: Optional[str] = None
    name: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = None


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
