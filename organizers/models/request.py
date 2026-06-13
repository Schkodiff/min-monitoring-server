from sqlmodel import Field, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from models.basemodel import EntityBaseModel
from models.enums import RequestStatus

class Request(EntityBaseModel, table=True):
    __tablename__ = "request"

    user_id: UUID = Field(index=True) #reg user
    poc_id: Optional[UUID] | None = Field(index=True) #admin/mod
    name: str
    inn: int = Field(index=True, unique=True)
    ogrn: int = Field(index=True, unique=True)
    phone: str = Field(unique=True)
    address: str = Field(unique=True)
    logo: str | None = Field(default_factory=uuid4, nullable=True)
    email: str = Field(index=True, unique=True)
    status: RequestStatus = Field(default=RequestStatus.pending, index=True)
    rejection_reason: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
