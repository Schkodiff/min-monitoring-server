from typing import Optional, List
from uuid import UUID
from .base_repository import BaseRepository
from sqlmodel import Session, select

from models.notification import Notification
from models.enums import NotificationType

class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)

    def get_by_type(self, session: Session, type: NotificationType) -> List[Notification]:
        return session.query(Notification).filter(Notification.type == type).all()