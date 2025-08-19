from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.project_service as service
from models.schemas import ProjectOut, ProjectOverviewOut, AssetOut, ShotOut

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
    return service.get_projects(db, uid=uid, name=name, limit=limit, offset=offset)


@router.get("/projects/{project_uid}/overview", response_model=ProjectOverviewOut)
def project_overview(project_uid: str, db: Session = Depends(get_db)):
    """List project overview by ID"""
    return service.get_project_overview(db, project_uid)


@router.get("/projects/{project_uid}/assets", response_model=list[AssetOut])
def list_project_assets(project_uid: str, db: Session = Depends(get_db)):
    """Returns all assets for a project"""
    assets = service.get_assets_by_project(db, project_uid)
    return assets


@router.get("/projects/{project_uid}/shots", response_model=list[ShotOut])
def list_project_shots(
        project_uid: str,
        seq: Optional[str] = None,
        shot: Optional[str] = None,
        range: Optional[str] = Query(None, description="Format: start-end (e.g. 100-200)"),
        db: Session = Depends(get_db),
):
    """Returns shots for a given project, with optional filtering."""

    try:
        return service.get_project_shots(db, project_uid, seq, shot, range)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
