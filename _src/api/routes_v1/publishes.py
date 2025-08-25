from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.publish_service as service
import models.schemas as schemas

router = APIRouter()


@router.get("/publishes", response_model=list[schemas.PublishOut])
def get_publishes(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        version_id: Optional[str] = None,
        type: Optional[str] = None,
        representation: Optional[str] = None,
        path: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Publishes with optional filters"""
    return service.list_publishes(db, uid, project_uid, version_id, type, representation, path, limit, offset)
