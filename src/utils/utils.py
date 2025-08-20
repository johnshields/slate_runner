import random
import string
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.models import Project, Asset


def generate_uid(prefix: str, length: int = 6) -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}_{suffix}"


def db_lookup(db: Session, model, uid: str):
    asset = db.scalar(select(model).where(model.uid == uid))
    if not asset:
        raise HTTPException(status_code=404, detail=f"{model.__name__} with UID '{uid}' not found.")
    return asset
