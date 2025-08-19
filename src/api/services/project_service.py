from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.models import Project, Shot, Task, Asset
from typing import Optional

from models.schemas import ProjectOverviewOut


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


def get_project_overview(db: Session, project_uid: str) -> ProjectOverviewOut:
    project = db.scalar(select(Project).where(Project.uid == project_uid))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    shots_count = db.scalar(select(func.count()).select_from(Shot).where(Shot.project_id == project_uid))

    tasks_count = db.scalar(
        select(func.count())
        .select_from(Task)
        .join(Shot, Task.parent_id == Shot.uid)
        .where(Task.parent_type == "shot", Shot.project_id == project_uid)
    )

    return ProjectOverviewOut(
        uid=project.uid,
        name=project.name,
        counts={"shots": shots_count, "tasks": tasks_count}
    )


def get_assets_by_project(db: Session, project_uid: str):
    stmt = select(Asset).where(Asset.project_id == project_uid).order_by(Asset.name.asc())
    return db.execute(stmt).scalars().all()
