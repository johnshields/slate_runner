from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.render import RenderJob
from models.project import Project
from schemas.render import RenderJobOut, RenderJobCreate, RenderJobUpdate
from typing import Optional
from utils import utils


# Get a list of render jobs with optional filtering (excluding soft-deleted)
def list_render_jobs(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        adapter: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
):
    stmt = select(RenderJob)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        stmt = stmt.where(RenderJob.deleted_at.is_(None))

    if uid:
        stmt = stmt.where(RenderJob.uid == uid)

    if project_uid:
        stmt = stmt.where(RenderJob.project_uid == project_uid)

    if adapter:
        stmt = stmt.where(RenderJob.adapter == adapter)

    if status:
        stmt = stmt.where(RenderJob.status == status)

    stmt = stmt.order_by(RenderJob.submitted_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# Create a new render job
def create_render_job(db: Session, data: RenderJobCreate) -> RenderJobOut:
    # Validate project exists
    project = utils.db_lookup(db, Project, data.project_uid)
    
    # Generate UID if not provided
    uid = data.uid or utils.generate_uid("RJ")
    
    # Create and persist render job
    new_render_job = RenderJob(
        uid=uid,
        project_uid=project.uid,
        context=data.context,
        adapter=data.adapter,
        status=data.status,
    )
    
    db.add(new_render_job)
    db.commit()
    db.refresh(new_render_job)
    
    return new_render_job


# Update a render job by UID
def update_render_job(db: Session, uid: str, data: RenderJobUpdate) -> RenderJobOut:
    # Locate render job by UID
    render_job = utils.db_lookup(db, RenderJob, uid)
    
    # Update fields if provided
    if data.context is not None:
        render_job.context = data.context
    
    if data.adapter is not None:
        render_job.adapter = data.adapter
    
    if data.status is not None:
        render_job.status = data.status
    
    if data.logs is not None:
        render_job.logs = data.logs
    
    db.commit()
    db.refresh(render_job)
    return render_job


# Delete a render job by UID (soft delete)
def delete_render_job(db: Session, uid: str) -> dict:
    from datetime import datetime, timezone
    
    render_job = utils.db_lookup(db, RenderJob, uid)
    
    # Soft delete: set deleted_at timestamp
    render_job.deleted_at = datetime.now(timezone.utc)
    
    db.commit()
    return {"detail": f"Render job '{uid}' deleted successfully"}
