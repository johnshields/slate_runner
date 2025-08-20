from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Task
from typing import Optional


# Get a list of all tasks, with optional filtering
def list_tasks(
        db: Session,
        uid: Optional[str] = None,
        project_id: Optional[str] = None,
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

    if project_id:
        stmt = stmt.where(Task.project_id == project_id)

    if parent_type:
        stmt = stmt.where(Task.parent_type == parent_type)

    if parent_id:
        stmt = stmt.where(Task.parent_id == parent_id)

    if name:
        stmt = stmt.where(Task.name.ilike(f"%{name}%"))

    if assignee:
        stmt = stmt.where(Task.assignee == assignee)

    if status:
        stmt = stmt.where(Task.status == status)

    stmt = stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
