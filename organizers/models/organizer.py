from sqlmodel import Field, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from models.basemodel import EntityBaseModel

if TYPE_CHECKING:
    from .orgUser import OrgUsersLink

class Organizer(EntityBaseModel, table=True):
    __tablename__ = "organizer"

    name: str = Field(index=True)
    inn: int = Field(unique=True, index=True)
    ogrn: int = Field(unique=True, index=True)
    phone: str = Field(unique=True, index=True)
    address: str = Field(unique=True, index=True)
    logo: str | None = Field(default_factory=uuid4)
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    #owner?

    #employees: List[UUID] = Relationship(back_populates="organizer", link_model=OrgUsersLink) #посмотреть как работает с бд с линк таблицами
    employees: List["OrgUsersLink"] = Relationship(back_populates="organizer")