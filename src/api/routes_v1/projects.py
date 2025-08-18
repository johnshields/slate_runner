from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from db.db import get_db
from api.services.project_service import get_shot_and_task_counts, get_latest_comp_movs, get_project_by_id
from models.models import Project
from models.schemas import ProjectOut

router = APIRouter()


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
        name: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """Returns a list of Projects"""

    stmt = select(Project)
    if name:
        stmt = stmt.where(Project.name == name)

    stmt = stmt.order_by(Project.name.asc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


@router.get("/projects/{project_id}/overview")
def project_overview(project_id: str, db: Session = Depends(get_db)):
    prj = get_project_by_id(db, project_id)

    if not prj:
        raise HTTPException(404, "project not found")

    shots_count, tasks_count = get_shot_and_task_counts(db, project_id)
    latest_comp = get_latest_comp_movs(db, project_id)

    return {
        "project": {"id": prj.uid, "name": prj.name},
        "counts": {"shots": shots_count, "tasks": tasks_count},
        "latest_comp_mov": latest_comp,
    }
