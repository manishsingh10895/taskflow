from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Integer
from datetime import datetime, timezone
import shared.db as db


class BaseModel(db.Base):
    __abstract__ = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="user")
    projects = relationship("Project", back_populates="user")


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, default="")
    bio = Column(String, default="")
    avatar_url = Column(String, default="")


class Task(BaseModel):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    project = relationship("Project", back_populates="tasks", foreign_keys=[project_id])

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "user_id": self.user_id,
            "project_id": self.project_id,
        }


class Project(BaseModel):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

    def __init__(self, name: str, description: str, user_id: int):
        self.name = name
        self.description = description
        self.user_id = user_id

    def to_dict(self):
        obj = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
        }

        if self.tasks:
            obj["tasks"] = [task.to_dict() for task in self.tasks]

        return obj
