from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Text, CheckConstraint, UniqueConstraint, TIMESTAMP, func
from typing import Optional, Dict, Any
from datetime import datetime


class Base(DeclarativeBase): pass


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[str] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("project_uid", "name", name="uq_asset_project_name"),)


class Shot(Base):
    __tablename__ = "shots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[str] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    seq: Mapped[str] = mapped_column(String, nullable=False)
    shot: Mapped[str] = mapped_column(String, nullable=False)
    frame_in: Mapped[int] = mapped_column(Integer, nullable=False)
    frame_out: Mapped[int] = mapped_column(Integer, nullable=False)
    fps: Mapped[Optional[float]] = mapped_column(nullable=True)
    colorspace: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("project_uid", "seq", "shot", name="uq_shot_code"),)


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[str] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    parent_type: Mapped[str] = mapped_column(String, nullable=False)
    parent_uid: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    assignee: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="WIP")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (CheckConstraint("parent_type IN ('asset','shot')", name="ck_task_parent_type"),)


class Version(Base):
    __tablename__ = "versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[Optional[str]] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=True)
    task_uid: Mapped[str] = mapped_column(ForeignKey("tasks.uid", ondelete="CASCADE"), nullable=False)
    vnum: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("task_uid", "vnum", name="uq_version_per_task"),)


class Publish(Base):
    __tablename__ = "publishes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    version_uid: Mapped[str] = mapped_column(ForeignKey("versions.uid", ondelete="CASCADE"), nullable=False)
    project_uid: Mapped[Optional[str]] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    representation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class RenderJob(Base):
    __tablename__ = "render_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[Optional[str]] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=True)
    context: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    adapter: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="queued")
    logs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (
        CheckConstraint("status IN ('queued','running','succeeded','failed')", name="ck_render_jobs_status", ),)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[Optional[str]] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
