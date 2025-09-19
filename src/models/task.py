from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func, CheckConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from enums.enums import ParentType, TaskStatus


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[str] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    parent_type: Mapped[ParentType] = mapped_column(Enum(ParentType), nullable=False)
    parent_uid: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    assignee: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.WIP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
