from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Shot, Project
from typing import Optional

from models.schemas import ShotOut, ShotCreate
from utils import utils


# Create a new shot, generate a UID if not provided.
def create_shot(db: Session, data: ShotCreate) -> ShotOut:
    # check if project exists
    project = db.scalar(select(Project).where(Project.uid == data.project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create and persist shot
    uid = data.uid or utils.generate_uid("SHOT")
    new_shot = Shot(
        uid=uid,
        project_id=project.uid,
        shot=data.shot,
        seq=data.seq,
        frame_in=data.frame_in,
        frame_out=data.frame_out,
        fps=data.fps,
        colorspace=data.colorspace,
    )
    db.add(new_shot)
    db.commit()
    db.refresh(new_shot)

    return new_shot


# Get a list of tasks versions, with optional filtering
def list_shots(
        db: Session,
        uid: Optional[str] = None,
        project_id: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Shot)

    if uid:
        stmt = stmt.where(Shot.uid == uid)

    if project_id:
        stmt = stmt.where(Shot.project_id == project_id)

    if shot:
        stmt = stmt.where(Shot.shot.ilike(f"%{shot}%"))

    stmt = stmt.order_by(Shot.shot.asc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
