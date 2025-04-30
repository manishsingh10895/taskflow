from fastapi import FastAPI, Depends, HTTPException, status, Request
from services.notification.app.schemas import NotificationResponse
import shared.db as db
from shared.middlewares.auth_header import TFAuthMiddleware
from sqlalchemy.orm import Session
from models import Notification

app = FastAPI()

app.add_middleware(TFAuthMiddleware)

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@app.get("/notifications", response_model=NotificationResponse)
def get_notifications(
    request: Request,
    session: Session = Depends(get_db),
):
    notifications = (
        session.query(Notification)
        .filter(Notification.user_id == request.state.user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return NotificationResponse(
        notifications=notifications,
        total=len(notifications),
    )


@app.put("/notifications/{notification_id}")
def mark_notification_as_read(
    request: Request,
    notification_id: int,
    session: Session = Depends(get_db),
):
    notification = (
        session.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == request.state.user_id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    notification.is_read = True
    session.commit()

    return {
        "message": "Notification marked as read",
        "notification_id": notification_id,
    }
