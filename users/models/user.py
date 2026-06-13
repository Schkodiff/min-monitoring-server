from sqlmodel import Field, Relationship
from pydantic import field_validator
from typing import Any, List, Optional
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from models.basemodel import EntityBaseModel


class UserRole(str, Enum):
    organizer = "organizer"
    participant = "participant"
    admin = "admin"
    mod = "moderator"


class User(EntityBaseModel, table=True):
    __tablename__ = "user"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(unique=True, index=True)
    password: str
    role: UserRole = Field(default=UserRole.participant)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    telegram_id: Optional[int] = Field(unique=True, index=True)
    telegram_code: Optional[str] = Field(unique=True, index=True)