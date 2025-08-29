from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Event
from typing import Optional


def list_events(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        kind: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Event)

    if uid:
        stmt = stmt.where(Event.uid == uid)

    if project_uid:
        stmt = stmt.where(Event.project_uid == project_uid)

    if kind:
        stmt = stmt.where(Event.kind == kind)

    stmt = stmt.order_by(Event.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
