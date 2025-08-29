from fastapi import HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Task, Version, Project
from typing import Optional

from models.schemas import TaskCreate, TaskUpdate, TaskOut
from utils import utils

TASK_DEFAULT_STATUS = "WIP"
VERSION_DEFAULT_STATUS = "draft"


# Create a new task, generate a UID if not provided, and auto-create Version v1.
def create_task(db: Session, data: TaskCreate, *, created_by: str | None = None) -> TaskOut:
    # check if project exists
    project = utils.db_lookup(db, Project, data.project_uid)

    # Create and persist task
    uid = data.uid or utils.generate_uid("TASK")
    new_task = Task(
        uid=uid,
        project_uid=project.uid,
        parent_type=data.parent_type,
        parent_uid=data.parent_uid,
        name=data.name,
        assignee=data.assignee,
        status=data.status or TASK_DEFAULT_STATUS,
    )

    try:
        # Flush to validate task constraints
        db.add(new_task)
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Task violates a database constraint") from e

    try:
        # Auto-create initial version (v1) for the task (defaults to 'draft')
        create_task_version(
            db,
            task=new_task,
            status=VERSION_DEFAULT_STATUS,
            created_by=created_by or new_task.assignee,
            vnum=1,
        )
        # Flush to validate version constraints only
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create initial version") from e

    # Commit both task and version atomically
    db.commit()
    db.refresh(new_task)
    return new_task


# Helper: create a version for a given task (defaults to 'draft', v1 unless overridden).
def create_task_version(
        db: Session,
        *,
        task: Task,
        status: str = VERSION_DEFAULT_STATUS,
        created_by: str | None = None,
        vnum: int = 1,
) -> Version:
    ver = Version(
        uid=utils.generate_uid("VER"),
        project_uid=task.project_uid,
        task_uid=task.uid,
        vnum=vnum,
        status=status,
        created_by=created_by,
    )
    db.add(ver)
    return ver


# Update a task by UID
def update_task(db: Session, uid: str, data: TaskUpdate) -> TaskOut:
    # Find task by UID
    task = utils.db_lookup(db, Task, uid)

    # Optionally update project association if project_uid is provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        task.project_uid = project.uid

    # Update other fields if provided
    if data.parent_type is not None:
        task.parent_type = data.parent_type

    if data.parent_uid is not None:
        task.parent_uid = data.parent_uid

    if data.name is not None:
        task.name = data.name

    if data.assignee is not None:
        task.assignee = data.assignee

    if data.status is not None:
        task.status = data.status

    db.commit()
    db.refresh(task)
    return task


# Delete a task by UID or name
def delete_task(db: Session, uid: str) -> dict:
    task = utils.db_lookup(db, Task, uid)

    db.delete(task)
    db.commit()
    return {"detail": f"Task '{uid}' deleted successfully"}


# Get a list of all tasks, with optional filtering
def list_tasks(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        parent_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        name: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Task)

    if uid:
        stmt = stmt.where(Task.uid == uid)

    if project_uid:
        stmt = stmt.where(Task.project_uid == project_uid)

    if parent_type:
        stmt = stmt.where(Task.parent_type == parent_type)

    if parent_id:
        stmt = stmt.where(Task.parent_uid == parent_id)

    if name:
        stmt = stmt.where(Task.name.ilike(f"%{name}%"))

    if assignee:
        stmt = stmt.where(Task.assignee == assignee)

    if status:
        stmt = stmt.where(Task.status == status)

    stmt = stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


def list_task_versions(
        db: Session,
        task_uid: str,
):
    utils.db_lookup(db, Task, task_uid)

    stmt = (
        select(Version)
        .where(Version.task_uid == task_uid)
        .order_by(Version.vnum.desc(), Version.created_at.desc())
    )
    return db.execute(stmt).scalars().all()
