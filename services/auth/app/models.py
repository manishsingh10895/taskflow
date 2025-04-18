from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Integer
from datetime import datetime, timezone
from db import Base


class BaseModel(Base):
    __abstract__ = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
