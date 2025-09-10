from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.version_service as service
import models.schemas as schemas

router = APIRouter()


@router.post("/versions", response_model=schemas.VersionOut, status_code=201)
def post_version(
        data: schemas.VersionCreate,
        db: Session = Depends(get_db),
        publish: bool = Query(default=False, description="Also create an initial publish"),
):
    """Create a new Version - optionally auto creates a publish."""
    return service.create_version(db, data, publish=publish)


@router.get("/versions", response_model=list[schemas.VersionOut])
def get_versions(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        task_id: Optional[str] = None,
        vnum: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Versions with optional filters."""
    return service.list_versions(db, uid, project_uid, task_id, vnum, status, created_by, limit, offset)
