from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.models import Project, Asset, Shot, Task, Publish
from typing import Optional
from models.schemas import ProjectOverviewOut, ProjectCreate, ProjectOut, ProjectUpdate
import utils.utils as utils


# Create a new project, generate a UID if not provided
def create_project(db: Session, data: ProjectCreate) -> ProjectOut:
    # Check if a project with the same name already exists
    if db.scalar(select(Project).where(Project.name == data.name)):
        raise HTTPException(
            status_code=409,
            detail=f"Project '{data.name}' already exists."
        )

    # Create and persist project
    uid = data.uid or utils.generate_uid("PROJ")
    new_project = Project(uid=uid, name=data.name)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# Update a project by UID or name
def update_project(db: Session, identifier: str, data: ProjectUpdate) -> ProjectOut:
    stmt = select(Project).where((Project.uid == identifier) | (Project.name == identifier))
    project = db.scalar(stmt)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if data.name:
        project.name = data.name

    db.commit()
    db.refresh(project)
    return project


# Delete a project by UID or name
def delete_project(db: Session, identifier: str) -> dict:
    stmt = select(Project).where((Project.uid == identifier) | (Project.name == identifier))
    project = db.scalar(stmt)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"detail": f"Project '{identifier}' deleted successfully"}


# Get a list of all projects, with optional filtering by UID or name
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


# Get basic counts and info for a single project
def list_project_overview(db: Session, project_uid: str) -> ProjectOverviewOut:
    project = db.scalar(select(Project).where(Project.uid == project_uid))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Count shots and tasks for the project
    shots_count = db.scalar(select(func.count()).select_from(Shot).where(Shot.project_id == project_uid))
    tasks_count = db.scalar(
        select(func.count()).select_from(Task).where(
            Task.project_id == project_uid,
            Task.parent_type == "shot"
        )
    )

    return ProjectOverviewOut(
        uid=project.uid,
        name=project.name,
        counts={"shots": shots_count, "tasks": tasks_count},
        created_at=project.created_at
    )


# Get all assets belonging to a project
def list_project_assets(
        db: Session,
        project_uid: str
):
    stmt = select(Asset).where(Asset.project_id == project_uid).order_by(Asset.name.asc())
    return db.execute(stmt).scalars().all()


# Get all shots in a project, with optional filtering by seq, shot, or frame range
def list_project_shots(
        db: Session,
        project_uid: str,
        seq: str = None,
        shot: str = None,
        range: str = None
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


# Get all tasks for a project, with optional filters for parent_type and status
def list_project_tasks(
        db: Session,
        project_uid: str,
        parent_type: Optional[str] = None,
        status: Optional[str] = None,
):
    stmt = select(Task).where(Task.project_id == project_uid)

    if parent_type:
        stmt = stmt.where(Task.parent_type == parent_type)

    if status:
        stmt = stmt.where(Task.status == status)

    return db.execute(stmt).scalars().all()


# Get all publishes for a project, optionally filtered by type and representation
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
