from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db import get_db
import api.services.asset_service as service
import models.schemas as schemas

router = APIRouter()


@router.post("/assets", response_model=schemas.AssetOut, status_code=201)
def create_asset(
        data: schemas.AssetCreate,
        db: Session = Depends(get_db)
):
    """Create a new Asset"""
    return service.create_asset(db, data)


@router.patch("/assets/{identifier}", response_model=schemas.AssetOut)
def patch_asset(
        identifier: str,
        data: schemas.AssetUpdate,
        db: Session = Depends(get_db),
):
    """Update an Asset by UID or Name"""
    return service.update_asset(db, identifier, data)


@router.delete("/assets/{identifier}")
def delete_asset(
        identifier: str,
        db: Session = Depends(get_db),
):
    """Delete an Asset by UID or Name"""
    return service.delete_asset(db, identifier)
