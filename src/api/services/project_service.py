from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.models import Project, Shot, Task


def get_project_by_id(db: Session, project_id: str):
    return db.scalar(select(Project).where(Project.uid == project_id))


def get_shot_and_task_counts(db: Session, project_id: str):
    shots_count = db.scalar(
        select(func.count()).select_from(Shot).where(Shot.project_id == project_id)
    )

    tasks_count = db.scalar(
        select(func.count()).select_from(Task)
        .join(Shot, Task.parent_id == Shot.uid)
        .where(Task.parent_type == "shot", Shot.project_id == project_id)
    )

    return shots_count, tasks_count


def get_latest_comp_movs(db: Session, project_id: str) -> list[dict]:
    return []
