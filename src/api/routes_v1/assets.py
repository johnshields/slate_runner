from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db import get_db
import api.services.asset_service as service
import schemas.asset
import schemas.task

router = APIRouter()


@router.post("/assets", response_model=schemas.asset.AssetOut, status_code=201)
def post_asset(
        data: schemas.asset.AssetCreate,
        db: Session = Depends(get_db)
):
    """Create a new Asset"""
    return service.create_asset(db, data)


@router.patch("/assets/{identifier}", response_model=schemas.asset.AssetOut)
def patch_asset(
        identifier: str,
        data: schemas.asset.AssetUpdate,
        db: Session = Depends(get_db),
):
    """Update an Asset by UID or Name."""
    return service.update_asset(db, identifier, data)


@router.delete("/assets/{identifier}")
def delete_asset(
        identifier: str,
        db: Session = Depends(get_db),
):
    """Delete an Asset by UID or Name."""
    return service.delete_asset(db, identifier)


@router.get("/assets", response_model=list[schemas.asset.AssetOut])
def get_assets(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        db: Session = Depends(get_db)
):
    """List or search Shots with optional filters."""
    return service.list_assets(db, uid, project_uid, name, type, limit, offset)


@router.get("/assets/{asset_uid}/tasks", response_model=list[schemas.task.TaskOut])
def get_asset_tasks(
        asset_uid: str,
        db: Session = Depends(get_db)
):
    """Returns all Tasks for an Asset."""
    return service.list_asset_tasks(db, asset_uid)
