from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
from api.services.project_service import get_projects, get_project_overview
from models.schemas import ProjectOut, ProjectOverviewOut

router = APIRouter()


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
        uid: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search projects by ID or name"""
    return get_projects(db, uid=uid, name=name, limit=limit, offset=offset)


@router.get("/projects/{project_uid}/overview", response_model=ProjectOverviewOut)
def project_overview(
        project_uid: str,
        db: Session = Depends(get_db)
):
    """List project overview by ID"""
    return get_project_overview(db, project_uid)
