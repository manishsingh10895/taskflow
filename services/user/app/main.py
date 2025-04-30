import grp
import os
import profile
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from services.user.app import schemas
from shared.middlewares.auth_header import TFAuthMiddleware
from services.user.app.schemas import FullUserResponse
from shared import db
from shared.models import User, UserProfile
from sqlalchemy.orm import Session
import grpc
from shared.grpc import auth_pb2, auth_pb2_grpc
from shared.logger import logger
import redis
import json
import typing
from fastapi import Body

app = FastAPI()


AUTH_GRPC_HOST = os.getenv("AUTH_GRPC_HOST", "localhost:50051")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


app.add_middleware(TFAuthMiddleware)


def get_user_info(user_id: int) -> typing.Optional[dict]:
    # try first from redis cache
    user_info = redis_client.get(f"user:{user_id}")

    if user_info:
        user_info = json.loads(user_info)
    else:
        # if not found in cache, get from grpc
        user_info = get_user_auth_grpc(user_id)

        # Remove password field if it exists
        if "password" in user_info:
            del user_info["password"]
        # store in redis cache for 1 hour
        redis_client.set(f"user:{user_id}", json.dumps(user_info), ex=3600)

    return user_info


def get_user_auth_grpc(user_id: int):
    channel = grpc.insecure_channel(AUTH_GRPC_HOST)
    stub = auth_pb2_grpc.AuthServiceStub(channel)

    try:
        request = auth_pb2.UserRequest(user_id=user_id)
        response = stub.GetUserInfo(request)

        return {
            "user_id": response.user_id,
            "email": response.email,
            "username": response.username,
        }
    except grpc.RpcError as e:
        logger.info(f"gRPC error: {e.code()} - {e.details()}")
        raise HTTPException(
            status_code=500, detail=f"gRPC error: {e.code()} - {e.details()}"
        )


@app.get("/users/me", response_model=FullUserResponse)
def get_user_profile(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get the current user's profile.
    """
    # Simulate getting the user ID from the token
    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get erser info from gRPC service
    user_info = get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user profile from the database

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not user_profile:
        # create an empty profile if it doesn't exist
        user_profile = UserProfile(user_id=user_id)
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

    data = {
        "id": user_profile.id if user_profile else None,
        "email": user_info["email"],
        "username": user_info["username"],
        "full_name": user_profile.full_name if user_profile else None,
        "bio": user_profile.bio if user_profile else None,
        "avatar_url": user_profile.avatar_url if user_profile else None,
    }

    return FullUserResponse(**data)

@app.post("/users/profile", response_model=FullUserResponse)
def create_user_profile(
    request: Request,
    profile_data: schemas.UserProfileCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user profile.
    """
    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    existing_profile = (
        db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    )
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    user_profile = UserProfile(
        user_id=user_id,
        full_name=profile_data.get("full_name"),
        bio=profile_data.get("bio"),
        avatar_url=profile_data.get("avatar_url"),
    )
    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)

    return FullUserResponse(
        id=user_profile.id,
        email=None,  # Email can be fetched from gRPC if needed
        username=None,  # Username can be fetched from gRPC if needed
        full_name=user_profile.full_name,
        bio=user_profile.bio,
        avatar_url=user_profile.avatar_url,
    )


@app.put("/users/profile", response_model=FullUserResponse)
def update_user_profile(
    request: Request,
    profile_data: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing user profile.
    """
    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_info = get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    user_profile.full_name = profile_data.full_name if profile_data.full_name else user_profile.full_name
    user_profile.bio = profile_data.bio if profile_data.bio else user_profile.bio
    user_profile.avatar_url = profile_data.avatar_url if profile_data.avatar_url else user_profile.avatar_url

    db.commit()
    db.refresh(user_profile)

    return FullUserResponse(
        id=user_profile.id,
        user_id=user_info['user_id'],
        email=user_info['email'],  # Email can be fetched from gRPC if needed
        username=user_info['username'],  # Username can be fetched from gRPC if needed
        full_name=user_profile.full_name,
        bio=user_profile.bio,
        avatar_url=user_profile.avatar_url,
    )


@app.delete("/users/profile", response_model=dict)
def delete_user_profile(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Delete the current user's profile.
    """
    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(user_profile)
    db.commit()

    return {"detail": "Profile deleted successfully"}
