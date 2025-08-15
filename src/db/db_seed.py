#!/usr/bin/env python
"""
Seed Supabase Postgres with a minimal DEMO show for slate_runner.

- Reads DATABASE_URL, etc. from .env via src/config.py
- Safe to run multiple times (idempotent)
- Optional --reset to wipe core tables (careful!)
"""

from __future__ import annotations
import sys
import os
import argparse
from datetime import datetime, timezone

from src.config import settings

# Make 'src' importable when running from repo root
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import Session

from src.db.db import engine, SessionLocal
from src.models.models import Base, Project, Shot, Task, Version, Publish

DEMO_PROJECT = "DEMO"


def log(msg: str) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[seed {now}] {msg}")


def reset_db(session: Session) -> None:
    """
    Danger: wipes core tables. Only for local/dev demos.
    """
    log("Reset requested: truncating tables (publishes, versions, tasks, shots, assets?, projects, render_jobs, events)")
    # Respect FK order
    session.execute(text("TRUNCATE TABLE publishes RESTART IDENTITY CASCADE;"))
    session.execute(text("TRUNCATE TABLE versions RESTART IDENTITY CASCADE;"))
    session.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE;"))
    # optional: assets if you added that table
    try:
        session.execute(text("TRUNCATE TABLE assets RESTART IDENTITY CASCADE;"))
    except Exception:
        pass
    session.execute(text("TRUNCATE TABLE shots RESTART IDENTITY CASCADE;"))
    session.execute(text("TRUNCATE TABLE render_jobs RESTART IDENTITY CASCADE;"))
    session.execute(text("TRUNCATE TABLE events RESTART IDENTITY CASCADE;"))
    session.execute(text("TRUNCATE TABLE projects RESTART IDENTITY CASCADE;"))
    session.commit()


def ensure_schema() -> None:
    """
    Create tables if they don't exist yet.
    Safe on Supabase; no-op if already present.
    """
    Base.metadata.create_all(bind=engine)


def get_or_create_project(session: Session, name: str) -> Project:
    prj = session.query(Project).filter_by(name=name).first()
    if prj:
        return prj
    prj = Project(name=name)
    session.add(prj)
    session.commit()
    session.refresh(prj)
    return prj


def get_or_create_shot(
        session: Session,
        project_id: int,
        seq: str,
        shot: str,
        frame_in: int,
        frame_out: int,
        fps: float = 24.0,
        colorspace: str = "sRGB",
) -> Shot:
    row = (
        session.query(Shot)
        .filter_by(project_id=project_id, seq=seq, shot=shot)
        .first()
    )
    if row:
        # Update basics if changed (non-destructive)
        updated = False
        if row.frame_in != frame_in:
            row.frame_in = frame_in
            updated = True
        if row.frame_out != frame_out:
            row.frame_out = frame_out
            updated = True
        if (row.fps or 24.0) != fps:
            row.fps = fps
            updated = True
        if (row.colorspace or "") != colorspace:
            row.colorspace = colorspace
            updated = True
        if updated:
            session.commit()
        return row

    row = Shot(
        project_id=project_id,
        seq=seq,
        shot=shot,
        frame_in=frame_in,
        frame_out=frame_out,
        fps=fps,
        colorspace=colorspace,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def get_or_create_task(
        session: Session,
        parent_type: str,
        parent_id: int,
        name: str,
        assignee: str | None = None,
        status: str = "WIP",
) -> Task:
    row = (
        session.query(Task)
        .filter_by(parent_type=parent_type, parent_id=parent_id, name=name)
        .first()
    )
    if row:
        # light update
        changed = False
        if assignee and row.assignee != assignee:
            row.assignee = assignee
            changed = True
        if status and row.status != status:
            row.status = status
            changed = True
        if changed:
            session.commit()
        return row

    row = Task(
        parent_type=parent_type,
        parent_id=parent_id,
        name=name,
        assignee=assignee,
        status=status,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def create_version_if_missing(session: Session, task_id: int, vnum: int, created_by: str = "seed") -> Version:
    row = (
        session.query(Version)
        .filter_by(task_id=task_id, vnum=vnum)
        .first()
    )
    if row:
        return row
    row = Version(task_id=task_id, vnum=vnum, created_by=created_by, status="draft")
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def create_publish_if_missing(
        session: Session,
        version_id: int,
        typ: str,
        representation: str,
        path: str,
        metadata: dict | None = None,
) -> Publish:
    # "idempotent enough": unique by (version_id, type, path)
    existing = (
        session.query(Publish)
        .filter_by(version_id=version_id, type=typ, path=path)
        .first()
    )
    if existing:
        return existing
    row = Publish(
        version_id=version_id,
        type=typ,
        representation=representation,
        path=path,
        metadata=metadata or {},
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def seed(session: Session) -> None:
    log(f"Using DATABASE_URL = {settings.DATABASE_URL!r}")

    # Ensure tables exist (if you didn't run Alembic yet)
    ensure_schema()

    # Project
    prj = get_or_create_project(session, DEMO_PROJECT)
    log(f"Project ensured: {prj.id} {prj.name}")

    # Shots
    s010_010 = get_or_create_shot(session, prj.id, "010", "010", frame_in=1001, frame_out=1100, fps=24.0,
                                  colorspace="sRGB")
    s010_020 = get_or_create_shot(session, prj.id, "010", "020", frame_in=1001, frame_out=1120, fps=24.0,
                                  colorspace="sRGB")
    log(f"Shots ensured: {s010_010.seq}_{s010_010.shot}, {s010_020.seq}_{s010_020.shot}")

    # Tasks (asset/shot). We'll focus on shot tasks: layout/comp
    comp_task_010 = get_or_create_task(session, "shot", s010_010.id, "comp", assignee="comp_artist")
    layout_task_010 = get_or_create_task(session, "shot", s010_010.id, "layout", assignee="layout_artist")
    comp_task_020 = get_or_create_task(session, "shot", s010_020.id, "comp", assignee="comp_artist")

    # Versions
    v_layout_001 = create_version_if_missing(session, layout_task_010.id, 1, created_by="layout_artist")
    v_comp_001 = create_version_if_missing(session, comp_task_010.id, 1, created_by="comp_artist")
    v_comp_002 = create_version_if_missing(session, comp_task_010.id, 2, created_by="comp_artist")

    # Publishes
    # Example convention: /DEMO/010/010/comp/v002/comp_v002.mov
    create_publish_if_missing(
        session,
        version_id=v_layout_001.id,
        typ="camera",
        representation="abc",
        path="/DEMO/010/010/layout/v001/camera_v001.abc",
        metadata={"fps": 24.0, "colorspace": "sRGB"},
    )
    create_publish_if_missing(
        session,
        version_id=v_comp_001.id,
        typ="comp",
        representation="exr",
        path="/DEMO/010/010/comp/v001/comp_v001.exr",
        metadata={"res": "2048x1152", "fps": 24.0, "colorspace": "sRGB"},
    )
    create_publish_if_missing(
        session,
        version_id=v_comp_002.id,
        typ="comp",
        representation="mov",
        path="/DEMO/010/010/comp/v002/comp_v002.mov",
        metadata={"burnins": True, "res": "2048x1152", "fps": 24.0},
    )

    log("Seed complete.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Supabase Postgres for slate_runner DEMO")
    parser.add_argument("--reset", action="store_true", help="Wipe core tables before seeding (DANGER).")
    args = parser.parse_args()

    try:
        with SessionLocal() as session:
            if args.reset:
                reset_db(session)
            seed(session)
        return 0
    except OperationalError as e:
        log(f"DB connection failed. Check DATABASE_URL / SSL settings. Error: {e}")
        return 2
    except IntegrityError as e:
        log(f"Integrity error while seeding: {e}")
        return 3
    except Exception as e:
        log(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
