from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.render_service as service
import models.schemas as schemas

router = APIRouter()


@router.get("/renders", response_model=list[schemas.RenderJobOut])
def get_render_jobs(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        adapter: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Render Jobs with optional filters"""
    return service.list_render_jobs(db, uid, project_uid, adapter, status, limit, offset)
