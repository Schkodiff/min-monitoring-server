from pydantic import field_validator
from typing import Any, List, Optional
from datetime import datetime
from uuid import UUID

from models.basemodel import EntityBaseModel
from models.enums import NotificationType


class NotificationResponse(EntityBaseModel):
    type: NotificationType
    message: str
    author: Optional[UUID]
    receiver: UUID
    lottery_id: UUID
    created_at: datetime
    updated_at: datetime


class NotificationCreate(EntityBaseModel):
    type: NotificationType
    message: str
    author: Optional[UUID]
    receiver: UUID
    lottery_id: UUID


class NotificationUpdate(EntityBaseModel):
    type: Optional[NotificationType] = None
    message: Optional[str] = None
    author: Optional[UUID] = None
    receiver: Optional[UUID] = None
    lottery_id: Optional[UUID] = None

