from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.publish import Publish
from models.project import Project
from models.version import Version
from schemas.publish import PublishOut, PublishCreate, PublishUpdate
from typing import Optional
from utils import utils

# Create a new publish
def create_publish(db: Session, data: PublishCreate) -> PublishOut:
    # Validate project and version exist
    project = utils.db_lookup(db, Project, data.project_uid)
    version = utils.db_lookup(db, Version, data.version_uid)

    # Generate UID if not provided
    uid = data.uid or utils.generate_uid("PUB")
    
    # Create and persist publish
    new_publish = Publish(
        uid=uid,
        project_uid=project.uid,
        version_uid=version.uid,
        type=data.type,
        representation=data.representation,
        path=data.path,
        meta=data.meta or {},
    )
    
    db.add(new_publish)
    db.commit()
    db.refresh(new_publish)
    
    return new_publish


# Update a publish by UID
def update_publish(db: Session, uid: str, data: PublishUpdate) -> PublishOut:
    # Locate publish by UID
    publish = utils.db_lookup(db, Publish, uid)
    
    # Update fields if provided
    if data.type is not None:
        publish.type = data.type
    
    if data.representation is not None:
        publish.representation = data.representation
    
    if data.path is not None:
        publish.path = data.path
    
    if data.meta is not None:
        publish.meta = data.meta
    
    db.commit()
    db.refresh(publish)
    return publish


# Delete a publish by UID (soft delete)
def delete_publish(db: Session, uid: str) -> dict:
    from datetime import datetime, timezone
    
    publish = utils.db_lookup(db, Publish, uid)
    
    # Soft delete: set deleted_at timestamp
    publish.deleted_at = datetime.now(timezone.utc)
    
    db.commit()
    return {"detail": f"Publish '{uid}' deleted successfully"}


# Get a list of all publishes, with optional filtering (excluding soft-deleted)
def list_publishes(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        version_uid: Optional[str] = None,
        type: Optional[str] = None,
        representation: Optional[str] = None,
        path: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
):
    stmt = select(Publish)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        stmt = stmt.where(Publish.deleted_at.is_(None))

    if uid:
        stmt = stmt.where(Publish.uid == uid)

    if project_uid:
        stmt = stmt.where(Publish.project_uid == project_uid)

    if version_uid:
        stmt = stmt.where(Publish.version_uid == version_uid)

    if type:
        stmt = stmt.where(Publish.type == type)

    if representation:
        stmt = stmt.where(Publish.representation == representation)

    if path:
        stmt = stmt.where(Publish.path.ilike(f"%{path}%"))

    stmt = stmt.order_by(Publish.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
