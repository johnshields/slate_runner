from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enums.enums import ParentType, TaskStatus


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    parent_type: ParentType
    parent_uid: Optional[str] = None
    name: str
    assignee: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    parent_type: Optional[ParentType] = None
    parent_uid: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    assignee: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.WIP

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Task name cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    uid: Optional[str] = None
    project_uid: Optional[str] = None
    parent_type: Optional[ParentType] = None
    parent_uid: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    assignee: Optional[str] = None
    status: Optional[TaskStatus] = None
