"""
Notifications router
Endpoints for CRUD operations on notifications
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID

from database import db_service
from models import NotificationCreate, NotificationResponse, NotificationUpdate

router = APIRouter(
    prefix='/api/v1/notifications',
    tags=['Notifications'],
)

@router.post('/', response_model=NotificationResponse)
async def create_notification(notification: NotificationCreate):
    result = await db_service.create_notification(notification.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create notification')
    return result

@router.get('/{notification_id}', response_model=NotificationResponse)
async def get_notification(notification_id: UUID):
    result = await db_service.get_notification(str(notification_id))
    if not result:
        raise HTTPException(status_code=404, detail='Notification not found')
    return result

@router.get('/', response_model=List[NotificationResponse])
async def list_notifications(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await db_service.list_notifications(str(user_id), limit=limit, offset=offset)

@router.put('/{notification_id}', response_model=NotificationResponse)
async def update_notification(notification_id: UUID, notification_update: NotificationUpdate):
    update_data = {k: v for k, v in notification_update.model_dump().items() if v is not None}
    result = await db_service.update_notification(str(notification_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='Notification not found')
    return result

@router.delete('/{notification_id}', response_model=NotificationResponse)
async def delete_notification(notification_id: UUID):
    result = await db_service.delete_notification(str(notification_id))
    if not result:
        raise HTTPException(status_code=404, detail='Notification not found')
    return result
