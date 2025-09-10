from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Asset, Project, Task
from schemas.task import TaskOut
from schemas.asset import AssetOut, AssetCreate, AssetUpdate
import utils.utils as utils


# Create a new asset, generate a UID if not provided.
def create_asset(db: Session, data: AssetCreate) -> AssetOut:
    # check if project exists
    project = utils.db_lookup(db, Project, data.project_uid)

    # Check if asset with same name already exists in this project
    if db.scalar(select(Asset).where(Asset.project_uid == data.project_uid, Asset.name == data.name)):
        raise HTTPException(
            status_code=409,
            detail=f"Asset '{data.name}' already exists in project '{data.project_uid}'."
        )

    # Create and persist asset
    uid = data.uid or utils.generate_uid("ASSET")
    new_asset = Asset(uid=uid, project_uid=project.uid, name=data.name, type=data.type)
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return new_asset


# Update an asset by UID or name
def update_asset(db: Session, identifier: str, data: AssetUpdate) -> AssetOut:
    # Find asset by UID or name
    asset = utils.db_lookup(db, Asset, identifier)

    # Optionally update project association if project_uid is provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        asset.project_uid = project.uid

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
    asset = utils.db_lookup(db, Asset, identifier)

    db.delete(asset)
    db.commit()
    return {"detail": f"Asset '{identifier}' deleted successfully"}


# Get a list of all assets, with optional filtering
def list_assets(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Asset)

    if uid:
        stmt = stmt.where(Asset.uid == uid)

    if project_uid:
        stmt = stmt.where(Asset.project_uid == project_uid)

    if name:
        stmt = stmt.where(Asset.name.ilike(f"%{name}%"))

    if type:
        stmt = stmt.where(Asset.type == type)

    stmt = stmt.order_by(Asset.name.asc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# Get all tasks belonging to an asset
def list_asset_tasks(db: Session, asset_uid: str) -> list[TaskOut]:
    utils.db_lookup(db, Asset, asset_uid)

    stmt = select(Task).where(
        Task.parent_type == "asset", Task.parent_uid == asset_uid
    ).order_by(Task.name.asc())

    return db.execute(stmt).scalars().all()
