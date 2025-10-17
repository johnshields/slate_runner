from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
import api.controllers.publish_controller as controller
import schemas.publish

router = APIRouter()


@router.get("/publishes", response_model=list[schemas.publish.PublishOut])
def get_publishes(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        version_uid: Optional[str] = None,
        type: Optional[str] = None,
        representation: Optional[str] = None,
        path: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Publishes with optional filters (excludes soft-deleted by default)."""
    return controller.list_publishes(db, uid, project_uid, version_uid, type, representation, path, limit, offset, include_deleted)


@router.post("/publishes", response_model=schemas.publish.PublishOut, status_code=201)
def post_publish(
        data: schemas.publish.PublishCreate,
        db: Session = Depends(get_db)
):
    """Create a new Publish."""
    return controller.create_publish(db, data)


@router.patch("/publishes/{uid}", response_model=schemas.publish.PublishOut)
def patch_publish(
        uid: str,
        data: schemas.publish.PublishUpdate,
        db: Session = Depends(get_db),
):
    """Update a Publish by UID."""
    return controller.update_publish(db, uid, data)


@router.delete("/publishes/{uid}")
def delete_publish(
        uid: str,
        db: Session = Depends(get_db),
):
    """Delete a Publish by UID."""
    return controller.delete_publish(db, uid)
