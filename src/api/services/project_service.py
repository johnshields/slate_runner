from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.models import Project, Asset, Shot, Task, Publish
from typing import Optional

from models.schemas import ProjectOverviewOut


def list_projects(
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


def list_project_overview(db: Session, project_uid: str) -> ProjectOverviewOut:
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


def list_project_assets(
        db: Session,
        project_uid: str
):
    stmt = select(Asset).where(Asset.project_id == project_uid).order_by(Asset.name.asc())
    return db.execute(stmt).scalars().all()


def list_project_shots(
        db: Session,
        project_uid: str,
        seq: str = None, shot:
        str = None, range:
        str = None
):
    stmt = select(Shot).where(Shot.project_id == project_uid)

    if seq:
        stmt = stmt.where(Shot.seq == seq)
    if shot:
        stmt = stmt.where(Shot.shot == shot)
    if range:
        try:
            start, end = map(int, range.split("-"))
            stmt = stmt.where(Shot.frame_in >= start, Shot.frame_out <= end)
        except ValueError:
            raise ValueError("Invalid range format. Use start-end (e.g. 100-200).")

    stmt = stmt.order_by(Shot.seq.asc(), Shot.shot.asc())
    return db.execute(stmt).scalars().all()


def list_project_tasks(
        db: Session,
        project_uid: str,
        parent_type: Optional[str] = None,
        status: Optional[str] = None,
):
    stmt = select(Task)

    # Filter by parent_type if provided
    if parent_type:
        stmt = stmt.where(Task.parent_type == parent_type)

    # Filter by status if provided
    if status:
        stmt = stmt.where(Task.status == status)

    # Join to filter by project
    if parent_type == "asset":
        stmt = stmt.join(Asset, Task.parent_id == Asset.uid).where(Asset.project_id == project_uid)
    elif parent_type == "shot":
        stmt = stmt.join(Shot, Task.parent_id == Shot.uid).where(Shot.project_id == project_uid)
    else:
        # Join both if no parent_type is specified
        stmt = stmt.where(
            ((Task.parent_type == "asset") & Task.parent_id.in_(
                select(Asset.uid).where(Asset.project_id == project_uid)
            )) |
            ((Task.parent_type == "shot") & Task.parent_id.in_(
                select(Shot.uid).where(Shot.project_id == project_uid)
            ))
        )
    return db.execute(stmt).scalars().all()


def list_project_publishes(
        db: Session,
        project_uid: str,
        type: str = None,
        rep: str = None
):
    stmt = select(Publish).where(Publish.project_id == project_uid)

    if type:
        stmt = stmt.where(Publish.type == type)
    if rep:
        stmt = stmt.where(Publish.representation == rep)

    return db.execute(stmt).scalars().all()
