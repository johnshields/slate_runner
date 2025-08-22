from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.task_service as service
import models.schemas as schemas

router = APIRouter()


@router.get("/tasks", response_model=list[schemas.TaskOut])
def get_tasks(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        parent_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        name: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search tasks with optional filters"""
    return service.list_tasks(db, uid, project_uid, parent_type, parent_id, name, assignee, status, limit, offset)
