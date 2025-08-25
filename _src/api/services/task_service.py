from http.client import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Task, Version, Project
from typing import Optional

from models.schemas import TaskCreate, TaskUpdate, TaskOut
from utils import utils


# Create a new task, generate a UID if not provided.
def create_task(db: Session, data: TaskCreate) -> TaskOut:
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
        status=data.status or "WIP",
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# Update a task by UID (UID-only lookups)
def update_task(db: Session, uid: str, data: TaskUpdate) -> TaskOut:
    # Find task by UID only
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
