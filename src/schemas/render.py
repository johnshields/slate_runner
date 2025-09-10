from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, field_validator


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


class RenderJobCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    context: Dict[str, Any]
    adapter: str
    status: str = "pending"

    @field_validator("status")
    def validate_status(cls, v):
        if v.lower() not in {"pending", "running", "done", "failed"}:
            raise ValueError("Invalid render job status")
        return v


class RenderJobUpdate(BaseModel):
    uid: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    adapter: Optional[str] = None
    status: Optional[str] = None
    logs: Optional[str] = None
