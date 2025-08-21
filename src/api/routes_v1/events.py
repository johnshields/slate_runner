from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.event_service as service
import models.schemas as schemas

router = APIRouter()


@router.get("/events", response_model=list[schemas.EventOut])
def get_events(
        uid: Optional[str] = None,
        project_id: Optional[str] = None,
        kind: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Events"""
    return service.list_events(db, uid, project_id, kind, limit, offset)
