import shared.db as db
from shared.logger import logger
from models import Notification


def handle_new_task(task):
    """
    Handle a new notification.
    """
    # Process the notification

    session = db.SessionLocal()
    print(f"New notification received: {task}")
    try:
        # Assuming Notification is a SQLAlchemy model
        new_notification = Notification(
            user_id=task.user_id, message=task.message, is_read=False
        )
        session.add(new_notification)
        session.commit()
    except Exception as e:
        logger.error(f"Error saving notification: {e}")
        session.rollback()
    finally:
        session.close()


def handle_task_deleted(task):
    """
    Handle a task deleted notification.
    """
    # Process the task deleted notification
    print(f"Task deleted notification received: {task}")
    # Here you can implement the logic to handle task deletion notifications

    session = db.SessionLocal()

    try:
        new_notification = Notification(
            user_id=task.user_id,
            message=f"Task {task.task_id} has been deleted",
            is_read=False,
        )

        session.add(new_notification)
        session.commit()

    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        session.rollback()
    finally:
        session.close()
