from fastapi import HTTPException
import grpc
from schemas import ProjectCreate
from services.user.app.main import get_user_auth_grpc
from shared.grpc import task_pb2, task_pb2_grpc
from sqlalchemy.orm import Session
from shared.models import Task, Project

TASK_GRPC_HOST = "localhost:50052"


# CRUD operations
def get_project(db: Session, user_id, project_id: int):
    # Check if the project exists and belongs to the user
    project = _check_ownership(db, user_id, project_id)
    # Return the project as a dictionary
    return project.to_dict()


def get_projects(db: Session, user_id, skip: int = 0, limit: int = 10):

    projects = (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [project.to_dict() for project in projects]


def _check_ownership(db: Session, user_id, project_id: int):
    # Check if the project exists and belongs to the user
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def get_project_user_tasks(db: Session, user_id, project_id: int):
    channel = grpc.insecure_channel(TASK_GRPC_HOST)
    stub = task_pb2_grpc.TaskServiceStub(channel)

    try:
        request = task_pb2.GetTasksForUserProjectRequest(
            user_id=user_id, project_id=project_id
        )
        response = stub.GetTasksForUserProject(request)

        tasks = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "user_id": task.user_id,
                "project_id": task.project_id,
            }
            for task in response.tasks
        ]
        return tasks
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500, detail=f"gRPC error: {e.code()} - {e.details()}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def get_tasks_for_project(db: Session, user_id: int, project_id: int):
    project = _check_ownership(db, user_id, project_id)

    tasks = get_project_user_tasks(db, user_id, project_id)

    return tasks;


def create_project(db: Session, user_id, project: ProjectCreate):
    # Check if the project already exists
    existing_project = db.query(Project).filter(Project.name == project.name).first()

    if existing_project:
        raise HTTPException(status_code=400, detail="Project already exists")

    db_project = Project(
        name=project.name, description=project.description, user_id=user_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project
