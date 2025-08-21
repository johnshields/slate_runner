from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.version_service as service
import models.schemas as schemas

router = APIRouter()


@router.get("/versions", response_model=list[schemas.VersionOut])
def get_versions(
        uid: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        vnum: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Versions with optional filters"""
    return service.list_versions(
        db=db,
        uid=uid,
        project_id=project_id,
        task_id=task_id,
        vnum=vnum,
        status=status,
        created_by=created_by,
        limit=limit,
        offset=offset
    )
