from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.shot_service as service
import models.schemas as schemas

router = APIRouter()


@router.post("/shots", response_model=schemas.ShotOut, status_code=201)
def post_shot(
        data: schemas.ShotCreate,
        db: Session = Depends(get_db)
):
    """Create a new Shot."""
    return service.create_shot(db, data)


@router.patch("/shots/{shot_uid}", response_model=schemas.ShotOut)
def patch_shot(
        shot_uid: str,
        data: schemas.ShotUpdate,
        db: Session = Depends(get_db),
):
    """Update a shot by UID."""
    return service.update_shot(db, shot_uid, data)


@router.delete("/shots/{shot_uid}")
def delete_shot(
        shot_uid: str,
        db: Session = Depends(get_db),
):
    """Delete an Asset by UID."""
    return service.delete_shot(db, shot_uid)


@router.get("/shots", response_model=list[schemas.ShotOut])
def get_shots(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Shots with optional filters."""
    return service.list_shots(db, uid, project_uid, shot, limit, offset)
