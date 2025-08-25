from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from db.db import get_db
import api.services.task_service as service
import models.schemas as schemas

router = APIRouter()


@router.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def post_task(
        data: schemas.TaskCreate,
        db: Session = Depends(get_db),
):
    """Create a new Task."""
    return service.create_task(db, data)


@router.patch("/tasks/{uid}", response_model=schemas.TaskOut)
def patch_task(
        uid: str,
        data: schemas.TaskUpdate,
        db: Session = Depends(get_db),
):
    """Update a Task by UID."""
    return service.update_task(db, uid, data)


@router.delete("/tasks/{uid}")
def delete_task(
        uid: str,
        db: Session = Depends(get_db),
):
    """Delete a Task by UID."""
    return service.delete_task(db, uid)


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
    """List or search tasks with optional filters."""
    return service.list_tasks(db, uid, project_uid, parent_type, parent_id, name, assignee, status, limit, offset)


@router.get("/tasks/{task_uid}/versions", response_model=List[schemas.VersionOut])
def get_task_versions(
        task_uid: str,
        db: Session = Depends(get_db),
):
    """List all versions belonging to a task."""
    return service.list_task_versions(db, task_uid)
