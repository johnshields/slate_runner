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
    """Create a new Shot"""
    return service.create_shot(db, data)


@router.get("/shots", response_model=list[schemas.ShotOut])
def get_shots(
        uid: Optional[str] = None,
        project_id: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Shots with optional filters"""
    return service.list_shots(db, uid, project_id, shot, limit, offset)
