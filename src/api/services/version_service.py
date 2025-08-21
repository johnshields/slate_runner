from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Version
from typing import Optional


# Get a list of all versions, with optional filtering
def list_versions(
        db: Session,
        uid: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        vnum: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Version)

    if uid:
        stmt = stmt.where(Version.uid == uid)

    if project_id:
        stmt = stmt.where(Version.project_id == project_id)

    if task_id:
        stmt = stmt.where(Version.task_id == task_id)

    if vnum is not None:
        stmt = stmt.where(Version.vnum == vnum)

    if status:
        stmt = stmt.where(Version.status == status)

    if created_by:
        stmt = stmt.where(Version.created_by == created_by)

    stmt = stmt.order_by(Version.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
