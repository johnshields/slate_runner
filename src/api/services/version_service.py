from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
from api.services.task_service import VERSION_DEFAULT_STATUS
from models.publish import Publish
from models.version import Version
from models.task import Task
from models.project import Project
from schemas.version import VersionOut, VersionCreate, VersionUpdate
from utils import utils


def create_version(
        db: Session,
        data: VersionCreate,
        *,
        publish: bool = False,
        created_by: str | None = None,
) -> VersionOut:
    # Ensure project and task exist
    project = utils.db_lookup(db, Project, data.project_uid)
    task = utils.db_lookup(db, Task, data.task_uid)

    # Get next vnum if not provided
    if data.vnum is None:
        max_vnum = db.scalar(
            select(func.max(Version.vnum)).where(Version.task_uid == task.uid)
        )
        vnum = (max_vnum or 0) + 1
    else:
        vnum = data.vnum

    version = Version(
        uid=utils.generate_uid("VER"),
        project_uid=project.uid,
        task_uid=task.uid,
        vnum=vnum,
        status=data.status or VERSION_DEFAULT_STATUS,
        created_by=created_by,
    )

    db.add(version)
    db.flush()  # may raise if constraint violated explicitly

    if publish:
        publish = Publish(
            uid=utils.generate_uid("PUB"),
            project_uid=project.uid,
            version_uid=version.uid,
            type=data.publish_type,
            representation=data.representation,
            path=data.path or "",
            meta=data.meta or {},
        )
        db.add(publish)
        db.flush()

    db.commit()
    db.refresh(version)
    return version


# Update a version by UID
def update_version(db: Session, uid: str, data: VersionUpdate) -> VersionOut:
    # Find version by UID
    version = utils.db_lookup(db, Version, uid)

    # Optionally update project association if project_uid is provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        version.project_uid = project.uid

    # Optionally update task association if task_uid is provided
    if data.task_uid:
        task = db.scalar(select(Task).where(Task.uid == data.task_uid))
        if not task:
            raise HTTPException(status_code=404, detail="Target task not found")
        version.task_uid = task.uid

    # Update other fields if provided
    if data.status is not None:
        version.status = data.status

    if data.created_by is not None:
        version.created_by = data.created_by

    db.commit()
    db.refresh(version)
    return version


def delete_version(db: Session, uid: str) -> dict:
    from datetime import datetime, timezone
    
    version = utils.db_lookup(db, Version, uid)
    
    # Soft delete: set deleted_at timestamp
    version.deleted_at = datetime.now(timezone.utc)
    
    db.commit()
    return {"detail": f"Version '{uid}' deleted successfully"}


# Get a list of all versions, with optional filtering (excluding soft-deleted)
def list_versions(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        task_uid: Optional[str] = None,
        vnum: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
):
    stmt = select(Version)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        stmt = stmt.where(Version.deleted_at.is_(None))

    if uid:
        stmt = stmt.where(Version.uid == uid)
    if project_uid:
        stmt = stmt.where(Version.project_uid == project_uid)
    if task_uid:
        stmt = stmt.where(Version.task_uid == task_uid)
    if vnum is not None:
        stmt = stmt.where(Version.vnum == vnum)
    if status:
        stmt = stmt.where(Version.status == status)
    if created_by:
        stmt = stmt.where(Version.created_by == created_by)

    stmt = stmt.order_by(Version.created_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()
