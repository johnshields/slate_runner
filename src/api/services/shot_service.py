from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Shot, Project
from typing import Optional

from models.schemas import ShotOut, ShotCreate, ShotUpdate
from utils import utils


# Create a new shot, generate a UID if not provided.
def create_shot(db: Session, data: ShotCreate) -> ShotOut:
    # check if project exists
    project = db.scalar(select(Project).where(Project.uid == data.project_id))
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{data.project_id}' not found")

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


# Update a shot by UID
def update_shot(db: Session, uid: str, data: ShotUpdate) -> ShotOut:
    # Find shot by UID
    stmt = select(Shot).where((Shot.uid == uid))
    shot = db.scalar(stmt)

    if not shot:
        raise HTTPException(status_code=404, detail=f"Shot '{uid}' not found")

    # Optionally update project association if project_uid is provided
    if data.project_id:
        project = db.scalar(select(Project).where(Project.uid == data.project_id))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        shot.project_id = project.uid

    # Update other fields if provided
    if data.shot:
        shot.shot = data.shot
    if data.seq:
        shot.seq = data.seq
    if data.frame_in:
        shot.frame_in = data.frame_in
    if data.frame_out:
        shot.frame_out = data.frame_out
    if data.fps:
        shot.fps = data.fps
    if data.colorspace:
        shot.colorspace = data.colorspace

    db.commit()
    db.refresh(shot)
    return shot


# Delete a shot by UID
def delete_shot(db: Session, uid: str) -> dict:
    stmt = select(Shot).where((Shot.uid == uid))
    shot = db.scalar(stmt)

    if not shot:
        raise HTTPException(status_code=404, detail=f"Shot '{uid}' not found")

    db.delete(shot)
    db.commit()
    return {"detail": f"Shot '{uid}' deleted successfully"}


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
