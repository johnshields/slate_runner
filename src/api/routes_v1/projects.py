from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from db.db import get_db
from models.models import Project
from models.schemas import ProjectOut

router = APIRouter()


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
        name: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    """Returns a list of Projects"""

    stmt = select(Project)
    if name:
        stmt = stmt.where(Project.name == name)

    stmt = stmt.order_by(Project.name.asc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
