from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Asset, Project
from models.schemas import AssetCreate, AssetOut, AssetUpdate
import utils.utils as utils


# Create a new asset, generate a UID if not provided.
def create_asset(db: Session, data: AssetCreate) -> AssetOut:
    # check if project exists
    project = db.scalar(select(Project).where(Project.uid == data.project_uid))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if asset with same name already exists in this project
    if db.scalar(select(Asset).where(Asset.project_id == data.project_uid, Asset.name == data.name)):
        raise HTTPException(
            status_code=409,
            detail=f"Asset '{data.name}' already exists in project '{data.project_uid}'."
        )

    # Create and persist asset
    uid = data.uid or utils.generate_uid("ASSET")
    new_asset = Asset(uid=uid, project_id=project.uid, name=data.name, type=data.type)
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return new_asset


# Update an asset by UID or name
def update_asset(db: Session, identifier: str, data: AssetUpdate) -> AssetOut:
    # Find asset by UID or name
    stmt = select(Asset).where((Asset.uid == identifier) | (Asset.name == identifier))
    asset = db.scalar(stmt)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Optionally update project association if project_uid is provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        asset.project_id = project.uid

    # Update other fields if provided
    if data.name:
        asset.name = data.name
    if data.type:
        asset.type = data.type

    db.commit()
    db.refresh(asset)
    return asset


# Delete an asset by UID or name
def delete_asset(db: Session, identifier: str) -> dict:
    stmt = select(Asset).where((Asset.uid == identifier) | (Asset.name == identifier))
    project = db.scalar(stmt)

    if not project:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(project)
    db.commit()
    return {"detail": f"Asset '{identifier}' deleted successfully"}
