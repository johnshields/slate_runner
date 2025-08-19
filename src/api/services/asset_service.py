from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.models import Asset, Project
from models.schemas import AssetCreate, AssetOut
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
