from shared.models import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class Notification(BaseModel):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    message = Column(String, index=False)
    is_read = Column(Boolean, index=True, default=False)

    def __init__(self, user_id: int, message: str, is_read: bool = False):
        self.user_id = user_id
        self.message = message
        self.is_read = is_read

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "is_read": self.is_read,
        }
