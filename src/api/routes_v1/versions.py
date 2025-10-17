from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.version_service as service
import schemas.version

router = APIRouter()


@router.post("/versions", response_model=schemas.version.VersionOut, status_code=201)
def post_version(
        data: schemas.version.VersionCreate,
        db: Session = Depends(get_db),
        publish: bool = Query(default=False, description="Also create an initial publish"),
):
    """Create a new Version - optionally auto creates a publish."""
    return service.create_version(db, data, publish=publish)


@router.patch("/versions/{uid}", response_model=schemas.version.VersionOut)
def patch_version(
        uid: str,
        data: schemas.version.VersionUpdate,
        db: Session = Depends(get_db),
):
    """Update a Version by UID."""
    return service.update_version(db, uid, data)


@router.delete("/versions/{uid}")
def delete_version(
        uid: str,
        db: Session = Depends(get_db),
):
    """Delete a Version by UID."""
    return service.delete_version(db, uid)


@router.get("/versions", response_model=list[schemas.version.VersionOut])
def get_versions(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        task_uid: Optional[str] = None,
        vnum: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Versions with optional filters (excludes soft-deleted by default)."""
    return service.list_versions(db, uid, project_uid, task_uid, vnum, status, created_by, limit, offset, include_deleted)
