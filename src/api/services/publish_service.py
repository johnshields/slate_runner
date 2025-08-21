from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Publish
from typing import Optional


# Get a list of all publishes, with optional filtering
def list_publishes(
        db: Session,
        uid: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
        type: Optional[str] = None,
        representation: Optional[str] = None,
        path: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Publish)

    if uid:
        stmt = stmt.where(Publish.uid == uid)

    if project_id:
        stmt = stmt.where(Publish.project_id == project_id)

    if version_id:
        stmt = stmt.where(Publish.version_id == version_id)

    if type:
        stmt = stmt.where(Publish.type == type)

    if representation:
        stmt = stmt.where(Publish.representation == representation)

    if path:
        stmt = stmt.where(Publish.path.ilike(f"%{path}%"))

    stmt = stmt.order_by(Publish.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
