from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from db.db import get_db
import api.services.task_service as service
import schemas.task
import schemas.version

router = APIRouter()


@router.post("/tasks", response_model=schemas.task.TaskOut, status_code=201)
def post_task(
        data: schemas.task.TaskCreate,
        db: Session = Depends(get_db),
):
    """Create a new Task - auto creates a version."""
    return service.create_task(db, data)


@router.patch("/tasks/{uid}", response_model=schemas.task.TaskOut)
def patch_task(
        uid: str,
        data: schemas.task.TaskUpdate,
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


@router.get("/tasks", response_model=list[schemas.task.TaskOut])
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
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search tasks with optional filters (excludes soft-deleted by default)."""
    return service.list_tasks(db, uid, project_uid, parent_type, parent_id, name, assignee, status, limit, offset, include_deleted)


@router.get("/tasks/{task_uid}/versions", response_model=List[schemas.version.VersionOut])
def get_task_versions(
        task_uid: str,
        db: Session = Depends(get_db),
):
    """List all versions belonging to a task."""
    return service.list_task_versions(db, task_uid)
