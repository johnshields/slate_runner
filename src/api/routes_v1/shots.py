from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.shot_service as service
import schemas.shot

router = APIRouter()


@router.post("/shots", response_model=schemas.shot.ShotOut, status_code=201)
def post_shot(
        data: schemas.shot.ShotCreate,
        db: Session = Depends(get_db)
):
    """Create a new Shot."""
    return service.create_shot(db, data)


@router.patch("/shots/{shot_uid}", response_model=schemas.shot.ShotOut)
def patch_shot(
        shot_uid: str,
        data: schemas.shot.ShotUpdate,
        db: Session = Depends(get_db),
):
    """Update a Shot by UID."""
    return service.update_shot(db, shot_uid, data)


@router.delete("/shots/{shot_uid}")
def delete_shot(
        shot_uid: str,
        db: Session = Depends(get_db),
):
    """Delete a Shot by UID."""
    return service.delete_shot(db, shot_uid)


@router.get("/shots", response_model=list[schemas.shot.ShotOut])
def get_shots(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Shots with optional filters (excludes soft-deleted by default)."""
    return service.list_shots(db, uid, project_uid, shot, limit, offset, include_deleted)
