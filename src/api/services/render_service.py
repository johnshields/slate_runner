from sqlalchemy.orm import Session
from sqlalchemy import select
from models.render import RenderJob
from typing import Optional


# Get a list of render jobs with optional filtering
def list_render_jobs(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        adapter: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(RenderJob)

    if uid:
        stmt = stmt.where(RenderJob.uid == uid)

    if project_uid:
        stmt = stmt.where(RenderJob.project_uid == project_uid)

    if adapter:
        stmt = stmt.where(RenderJob.adapter == adapter)

    if status:
        stmt = stmt.where(RenderJob.status == status)

    stmt = stmt.order_by(RenderJob.uid.asc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
