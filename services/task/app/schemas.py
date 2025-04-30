# schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    completed: Optional[bool] = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    user_id: int
    completed: bool
    created_at: datetime

    class Config:
        orm_mode = True

class TaskStatsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int