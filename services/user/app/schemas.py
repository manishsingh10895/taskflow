from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str = ""
    bio: str = ""
    avatar_url: str = ""

    class Config:
        orm_mode = True


class FullUserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: str = ""
    bio: str = ""
    avatar_url: str = ""

    class Config:
        orm_mode = True


class UserProfileUpdate(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None

    class Config:
        orm_mode = True


class UserProfileCreate(BaseModel):
    bio: str
    avatar_url: str
    full_name: str

