from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Shot
from typing import Optional

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