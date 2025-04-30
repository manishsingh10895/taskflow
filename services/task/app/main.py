# main.py

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from google_crc32c import exc
from services.task.app import redis_helper
from shared.middlewares.auth_header import TFAuthMiddleware
from sqlalchemy.orm import Session
import shared.db as db
from shared.auth_utils import decode_token
from .schemas import TaskCreate, TaskStatsResponse, TaskUpdate, TaskResponse
from . import crud
import redis_helper as redis_helper
import pika, json
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(dotenv_path=env_path)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

app = FastAPI()

app.add_middleware(TFAuthMiddleware)


def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def publish_task_event(event_type: str, data: dict):
    connection = pika.BlockingConnection(
        pika.URLParameters("amqp://guest:guest@localhost:5672/")
    )
    channel = connection.channel()
    channel.queue_declare(queue="task_events", durable=True)

    channel.exchange_declare(exchange="notifications", exchange_type="topic")

    channel.basic_publish(
        exchange="notifications",
        routing_key=event_type,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )

    connection.close()


def get_user_id(authorization: str = Header(...)) -> int:
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    return int(payload.get("sub"))


@app.post("/tasks", response_model=TaskResponse)
def create(request: Request, task: TaskCreate, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    redis_helper.increment_task_count(user_id)
    if task.completed:
        redis_helper.increment_completed_task_count(user_id)
    else:
        redis_helper.increment_pending_task_count(user_id)

    # Publish task creation event
    publish_task_event("task.created", {"user_id": user_id, "task": task.model_dump()})

    return crud.create_task(db, task, user_id)


@app.get("/tasks", response_model=list[TaskResponse])
def task_list(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    return crud.get_tasks(db, user_id)


@app.get("/tasks/stats", response_model=TaskStatsResponse)
def task_stats(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    # Retrieve cached stats
    total_tasks = redis_helper.get_task_count(user_id)
    completed_tasks = redis_helper.get_completed_task_count(user_id)

    # If cache is missing, calculate from the database
    if total_tasks is None or completed_tasks is None:
        tasks = crud.get_tasks(db, user_id)
        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task.completed])

        # Update the cache
        redis_helper.set_task_count(user_id, total_tasks)
        redis_helper.set_completed_task_count(user_id, completed_tasks)

    pending_tasks = total_tasks - completed_tasks

    return TaskStatsResponse(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
    )


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update(
    request: Request, task_id: int, task: TaskUpdate, db: Session = Depends(get_db)
):
    user_id = request.state.user_id

    # Check if the task belongs to the user
    if not crud.check_task_ownership(db, task_id, user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task"
        )

    updated = crud.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update cache based on task completion status
    if task.completed:
        redis_helper.increment_completed_task_count(user_id)
    else:
        redis_helper.decrement_completed_task_count(user_id)

    return updated


@app.delete("/tasks/{task_id}")
def delete(request: Request, task_id: int, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    if not crud.check_task_ownership(db, task_id, user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this task"
        )

    deleted_task = crud.get_task(db, task_id)
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update cache before deletion
    redis_helper.decrement_task_count(user_id)
    if deleted_task.completed:
        redis_helper.decrement_completed_task_count(user_id)

    crud.delete_task(db, task_id)
    return {"status": "deleted"}
