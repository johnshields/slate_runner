from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


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


class VersionCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    task_uid: str
    vnum: Optional[int] = None
    status: Optional[str] = "draft"
    publish_type: Optional[str] = None
    representation: Optional[str] = None
    path: Optional[str] = None
    meta: Optional[dict] = {}

    @field_validator("status")
    def validate_status(cls, v):
        if v and v.lower() not in {"draft", "wip", "approved", "final"}:
            raise ValueError("Invalid version status")
        return v


class VersionUpdate(BaseModel):
    uid: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
