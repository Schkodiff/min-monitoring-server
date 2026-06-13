from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional

from models.enums import NotificationType, UserRole
from repositories.notification_repository import NotificationRepository
from schemas.notification import NotificationUpdate, NotificationResponse, NotificationCreate
from services.message_publisher import MessagePublisher


class NotificationService:
    def __init__(self, notifications: NotificationRepository, message_publisher: Optional[MessagePublisher] = None):
        self.notifications = notifications
        self.message_publisher = message_publisher

    def get_all_notifications(self, session: Session) -> List[NotificationResponse]:
        notifications = self.notifications.list_all(session)
        return [NotificationResponse.model_validate(notification) for notification in notifications]

    def get_notification(self, session: Session, notification_id: UUID) -> NotificationResponse:
        notification = self.notifications.get(session, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уведомление не найдено"
            )
        return NotificationResponse.model_validate(notification)
    
    def get_notifications_by_type(self, session: Session, notification_id: UUID, type: NotificationType) -> NotificationResponse:
        notifications = self.notifications.get_by_type(session, notification_id, type)
        if not notifications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уведомления данного типа не найдены"
            )
        return [NotificationResponse.model_validate(notification) for notification in notifications]

    def create_notification(self, session: Session, notification_create: NotificationCreate, current_user_role: UserRole) -> NotificationResponse:
        if current_user_role == UserRole.participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="At least organizator privileges required"
            )
        
        new_notification = self.notifications.create(session, notification_create)
        notification_response = NotificationResponse.model_validate(new_notification)
        
        if self.message_publisher:
            self.message_publisher.publish_notification_background(
                {
                    "id": str(new_notification.id),
                    "type": new_notification.type.value,
                    "message": new_notification.message,
                    "author": str(new_notification.author) if new_notification.author else None,
                    "receiver": str(new_notification.receiver),
                    "lottery_id": str(new_notification.lottery_id),
                    "created_at": new_notification.created_at.isoformat(),
                }
            )
        
        return notification_response

    def update_notification(self, session: Session, notification_id: UUID, notification_update: NotificationUpdate) -> NotificationResponse:
        notification = self.notifications.get(session, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уведомление не найдено"
            )
        
        updated_notification = self.notifications.update(session, notification_id, notification_update)
        return NotificationResponse.model_validate(updated_notification)

    def delete_notification(self, session: Session, notification_id: UUID) -> None:
        notification = self.notifications.get(session, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уведомление не найдено"
            )
        
        self.notifications.delete(session, notification_id)


def get_notification_service():
    return NotificationService(NotificationRepository())
