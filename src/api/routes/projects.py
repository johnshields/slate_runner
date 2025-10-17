from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
from enums.enums import PublishType, Representation, ParentType
import api.controllers.project_controller as controller
import schemas.asset
import schemas.project
import schemas.publish
import schemas.shot
import schemas.task

router = APIRouter()


@router.post("/projects", response_model=schemas.project.ProjectOut, status_code=201)
def post_project(
        data: schemas.project.ProjectCreate,
        db: Session = Depends(get_db)
):
    """Create a new Project."""
    return controller.create_project(db, data)


@router.patch("/projects/{identifier}", response_model=schemas.project.ProjectOut)
def patch_project(
        identifier: str,
        data: schemas.project.ProjectUpdate,
        db: Session = Depends(get_db),
):
    """Update a Project by UID or name."""
    return controller.update_project(db, identifier, data)


@router.delete("/projects/{identifier}")
def delete_project(
        identifier: str,
        db: Session = Depends(get_db),
):
    """Delete a Project by UID or name."""
    return controller.delete_project(db, identifier)


@router.get("/projects", response_model=list[schemas.project.ProjectOut])
def get_projects(
        uid: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Projects with optional filters (excludes soft-deleted by default)."""
    return controller.list_projects(db, uid, name, limit, offset, include_deleted)


@router.get("/projects/{project_uid}/overview", response_model=schemas.project.ProjectOverviewOut)
def project_overview(
        project_uid: str,
        db: Session = Depends(get_db)
):
    """Retrieve Project overview by UID."""
    return controller.list_project_overview(db, project_uid=project_uid)


@router.get("/projects/{project_uid}/assets", response_model=list[schemas.asset.AssetOut])
def get_project_assets(
        project_uid: str,
        db: Session = Depends(get_db)
):
    """List all Assets for a Project."""
    assets = controller.list_project_assets(db, project_uid)
    return assets


@router.get("/projects/{project_uid}/shots", response_model=list[schemas.shot.ShotOut])
def get_project_shots(
        project_uid: str,
        seq: Optional[str] = None,
        shot: Optional[str] = None,
        range: Optional[str] = Query(None, description="Format: start-end (e.g. 100-200)"),
        db: Session = Depends(get_db),
):
    """List Shots for a Project with optional filters."""

    try:
        return controller.list_project_shots(db, project_uid, seq, shot, range)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_uid}/tasks", response_model=list[schemas.task.TaskOut])
def get_project_tasks(
        project_uid: str,
        parent_type: Optional[ParentType] = Query(None),
        status: Optional[str] = None,
        db: Session = Depends(get_db),
):
    """List Project Tasks with optional filters."""
    return controller.list_project_tasks(db, project_uid, parent_type, status)


@router.get("/projects/{project_uid}/publishes", response_model=list[schemas.publish.PublishOut])
def get_project_publishes(
        project_uid: str,
        type: Optional[PublishType] = Query(None),
        rep: Optional[Representation] = Query(None),
        db: Session = Depends(get_db)
):
    """List Project Publishes with optional filters."""
    return controller.list_project_publishes(db, project_uid, type, rep)
