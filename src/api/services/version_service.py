from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
from api.services.task_service import VERSION_DEFAULT_STATUS
from models.models import Version, Publish, Task, Project
from schemas.version import VersionOut, VersionCreate
from utils import utils


def create_version(
        db: Session,
        data: VersionCreate,
        *,
        publish: bool = False,
        created_by: str | None = None,
) -> VersionOut:
    # Ensure project and task exist
    project = utils.db_lookup(db, Project, data.project_uid)
    task = utils.db_lookup(db, Task, data.task_uid)

    # Get next vnum if not provided
    if data.vnum is None:
        max_vnum = db.scalar(
            select(func.max(Version.vnum)).where(Version.task_uid == task.uid)
        )
        vnum = (max_vnum or 0) + 1
    else:
        vnum = data.vnum

    version = Version(
        uid=utils.generate_uid("VER"),
        project_uid=project.uid,
        task_uid=task.uid,
        vnum=vnum,
        status=data.status or VERSION_DEFAULT_STATUS,
        created_by=created_by,
    )

    db.add(version)
    db.flush()  # may raise if constraint violated explicitly

    if publish:
        publish = Publish(
            uid=utils.generate_uid("PUB"),
            project_uid=project.uid,
            version_uid=version.uid,
            type=data.publish_type,
            representation=data.representation,
            path=data.path or "",
            meta=data.meta or {},
        )
        db.add(publish)
        db.flush()

    db.commit()
    db.refresh(version)
    return version


# Get a list of all versions, with optional filtering
def list_versions(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        task_uid: Optional[str] = None,
        vnum: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
):
    stmt = select(Version)

    if uid:
        stmt = stmt.where(Version.uid == uid)

    if project_uid:
        stmt = stmt.where(Version.project_uid == project_uid)

    if task_uid:
        stmt = stmt.where(Version.task_id == task_uid)

    if vnum is not None:
        stmt = stmt.where(Version.vnum == vnum)

    if status:
        stmt = stmt.where(Version.status == status)

    if created_by:
        stmt = stmt.where(Version.created_by == created_by)

    stmt = stmt.order_by(Version.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
