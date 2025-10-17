from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.shot import Shot
from models.project import Project
from typing import Optional

from schemas.shot import ShotCreate, ShotUpdate, ShotOut
from utils import utils


# Create a new shot, generate a UID if not provided.
def create_shot(db: Session, data: ShotCreate) -> ShotOut:
    # check if project exists
    project = utils.db_lookup(db, Project, data.project_uid)

    # Create and persist shot
    uid = data.uid or utils.generate_uid("SHOT")
    new_shot = Shot(
        uid=uid,
        project_uid=project.uid,
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
    shot = utils.db_lookup(db, Shot, uid)

    # Optionally update project association if project_uid is provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
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


# Delete a shot by UID (soft delete)
def delete_shot(db: Session, uid: str) -> dict:
    from datetime import datetime, timezone
    
    shot = utils.db_lookup(db, Shot, uid)
    
    # Soft delete: set deleted_at timestamp
    shot.deleted_at = datetime.now(timezone.utc)
    
    db.commit()
    return {"detail": f"Shot '{uid}' deleted successfully"}


# Get a list of shots, with optional filtering (excluding soft-deleted)
def list_shots(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
):
    stmt = select(Shot)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        stmt = stmt.where(Shot.deleted_at.is_(None))

    if uid:
        stmt = stmt.where(Shot.uid == uid)

    if project_uid:
        stmt = stmt.where(Shot.project_uid == project_uid)

    if shot:
        stmt = stmt.where(Shot.shot.ilike(f"%{shot}%"))

    stmt = stmt.order_by(Shot.shot.asc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
