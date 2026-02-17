from fastapi import APIRouter, HTTPException, Header
from lib.models import NotificationListResponse, MessageResponse
from lib.notification_service import get_user_notifications, mark_notification_read
from lib.auth_service import require_user_id

router = APIRouter()

@router.get("/me", response_model=NotificationListResponse)
def my_notifications(authorization: str | None = Header(default=None)):
    try:
        user_id = require_user_id(authorization)
        notifications = get_user_notifications(user_id)
        return NotificationListResponse(notifications=notifications)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/user/{user_id}", response_model=NotificationListResponse)
def list_notifications(user_id: int):
    try:
        notifications = get_user_notifications(user_id)
        return NotificationListResponse(notifications=notifications)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{notification_id}/read", response_model=MessageResponse)
def mark_read(notification_id: int, authorization: str | None = Header(default=None)):
    try:
        require_user_id(authorization)
        mark_notification_read(notification_id)
        return MessageResponse(message="Notification marked as read")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
