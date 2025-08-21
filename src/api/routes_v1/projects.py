from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.services.project_service as service
import models.schemas as schemas

router = APIRouter()


@router.post("/projects", response_model=schemas.ProjectOut, status_code=201)
def post_project(
        data: schemas.ProjectCreate,
        db: Session = Depends(get_db)
):
    """Create a new Project"""
    return service.create_project(db, data)


@router.patch("/projects/{identifier}", response_model=schemas.ProjectOut)
def patch_project(
        identifier: str,
        data: schemas.ProjectUpdate,
        db: Session = Depends(get_db),
):
    """Update a Project by UID or Name"""
    return service.update_project(db, identifier, data)


@router.delete("/projects/{identifier}")
def delete_project(
        identifier: str,
        db: Session = Depends(get_db),
):
    """Delete a Project by UID or Name"""
    return service.delete_project(db, identifier)


@router.get("/projects", response_model=list[schemas.ProjectOut])
def get_projects(
        uid: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """List or search Projects by UID or name"""
    return service.list_projects(db, uid, name, limit, offset)


@router.get("/projects/{project_uid}/overview", response_model=schemas.ProjectOverviewOut)
def project_overview(
        project_uid: str,
        db: Session = Depends(get_db)
):
    """List Project overview by UID"""
    return service.list_project_overview(db, project_uid=project_uid)


@router.get("/projects/{project_uid}/assets", response_model=list[schemas.AssetOut])
def get_project_assets(
        project_uid: str,
        db: Session = Depends(get_db)
):
    """Returns all Assets for a Project"""
    assets = service.list_project_assets(db, project_uid)
    return assets


@router.get("/projects/{project_uid}/shots", response_model=list[schemas.ShotOut])
def get_project_shots(
        project_uid: str,
        seq: Optional[str] = None,
        shot: Optional[str] = None,
        range: Optional[str] = Query(None, description="Format: start-end (e.g. 100-200)"),
        db: Session = Depends(get_db),
):
    """Returns Shots for a given Project, with optional filtering."""

    try:
        return service.list_project_shots(db, project_uid, seq, shot, range)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_uid}/tasks", response_model=list[schemas.TaskOut])
def get_project_tasks(
        project_uid: str,
        parent_type: Optional[str] = Query(None, regex="^(asset|shot)$"),
        status: Optional[str] = None,
        db: Session = Depends(get_db),
):
    """Returns Project Tasks filtered by parent_type and status"""
    return service.list_project_tasks(db, project_uid, parent_type, status)


@router.get("/projects/{project_uid}/publishes", response_model=list[schemas.PublishOut])
def get_project_publishes(
        project_uid: str,
        type: Optional[str] = Query(None, regex="^(comp|geo)$"),
        rep: Optional[str] = Query(None, regex="^(mov|exr)$"),
        db: Session = Depends(get_db)
):
    """Returns Project Publishes filtered by type and representation"""
    return service.list_project_publishes(db, project_uid, type, rep)
