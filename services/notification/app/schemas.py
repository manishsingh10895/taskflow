from pydantic import BaseModel


class Notification(BaseModel):
    id: int
    user_id: int
    is_read: bool
    message: str
    created_at: str

    class Config:
        orm_mode = True


class NotificationResponse(BaseModel):
    notifications: list[Notification]
    total: int

    class Config:
        orm_mode = True
