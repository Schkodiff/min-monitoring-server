from sqlmodel import Field, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING, Any, List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.types import JSON

from models.basemodel import EntityBaseModel
from models.enums import LotteryStatus

if TYPE_CHECKING:
    from .prize import Prize
    from .ticket import Ticket


class Lottery(EntityBaseModel, table=True):
    __tablename__ = "lottery"

    name: str = Field(index=True)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime = Field(default_factory=datetime.utcnow)
    max_entries: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: LotteryStatus = Field(default=LotteryStatus.inactive)
    description: Optional[str] = None
    #img

    org_id: UUID = Field(index=True)

    prizes: List["Prize"] = Relationship(back_populates="lottery")
    tickets: List["Ticket"] = Relationship(back_populates="lottery")

    randomizer_result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
