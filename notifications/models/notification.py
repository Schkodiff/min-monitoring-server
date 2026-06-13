from sqlmodel import Field, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from models.basemodel import EntityBaseModel
from models.enums import NotificationType

class Notification(EntityBaseModel, table=True):
    __tablename__ = "notification"

    type: NotificationType = Field(index=True)
    message: str
    author: Optional[UUID] = Field(default=None)
    receiver: UUID
    lottery_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
