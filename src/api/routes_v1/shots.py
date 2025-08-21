from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.shot_service as service
import models.schemas as schemas

router = APIRouter()


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
    return service.list_shots(db, uid=uid, project_id=project_id, shot=shot, limit=limit, offset=offset)
