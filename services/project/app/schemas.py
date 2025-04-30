# Pydantic model for request/response
from turtle import title
from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = ""
    completed: bool = False
    created_at: datetime
    project_id: Optional[int] = None

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    description: str

class ProjectWithTasks(BaseModel):
    id: int
    name: str
    description: str
    tasks: Optional[TaskResponse] = []

    class Config:
        orm_mode = True

class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int

    class Config:
        orm_mode = True
