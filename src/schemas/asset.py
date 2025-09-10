from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    name: str = Field(..., min_length=1, max_length=100)
    type: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Asset name cannot be empty")
        return v.strip()


class AssetUpdate(BaseModel):
    uid: Optional[str] = None
    project_uid: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = None
