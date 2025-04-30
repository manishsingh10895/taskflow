# crud.py

from sqlalchemy.orm import Session
from .schemas import TaskCreate, TaskUpdate
from shared.models import Task


def create_task(db: Session, task: TaskCreate, user_id: int):
    db_task = Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id).all()


def check_task_ownership(db: Session, task_id: int, user_id: int):
    task = get_task(db, task_id)
    if not task:
        return False
    if task.user_id != user_id:
        return False

    return True


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task_id: int, task_data: TaskUpdate):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task
