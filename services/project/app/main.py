from fastapi import FastAPI, HTTPException, Depends, Request
from shared.middlewares.auth_header import TFAuthMiddleware
from sqlalchemy.orm import Session
from shared.db import Base, engine, SessionLocal
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from shared.models import Project
from schemas import ProjectCreate, TaskResponse, ProjectResponse
from crud import get_project, get_projects, create_project, get_tasks_for_project

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(TFAuthMiddleware)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API endpoints
@app.post("/projects/", response_model=ProjectResponse)
def create_project_endpoint(
    request: Request, project: ProjectCreate, db: Session = Depends(get_db)
):
    user_id = request.state.user_id

    return create_project(db, user_id, project)


@app.get("/projects/", response_model=list[ProjectResponse])
def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_projects(db, skip=skip, limit=limit)


@app.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
def get_tasks_for_project_api(
    request: Request,
    project_id: int, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    tasks = get_tasks_for_project(db, user_id, project_id)

    return tasks


@app.get("/projects/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project
