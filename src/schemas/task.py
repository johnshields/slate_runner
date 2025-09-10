﻿from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    name: str = Field(..., min_length=1, max_length=100)
    assignee: Optional[str] = None
    status: Optional[str] = "WIP"

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Task name cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    uid: Optional[str] = None
    project_uid: Optional[str] = None
    parent_type: Optional[Literal["asset", "shot"]] = None
    parent_uid: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    assignee: Optional[str] = None
    status: Optional[str] = None
