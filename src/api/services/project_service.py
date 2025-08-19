from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.models import Project, Shot, Task
from typing import Optional


def get_projects(
        db: Session,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Project)

    if uid:
        stmt = stmt.where(Project.uid == uid)

    if name:
        stmt = stmt.where(Project.name.ilike(f"%{name}%"))

    stmt = stmt.order_by(Project.name.asc()).limit(limit).offset(offset)

    return db.execute(stmt).scalars().all()
