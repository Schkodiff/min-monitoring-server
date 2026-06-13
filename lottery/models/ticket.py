from enum import Enum
from sqlmodel import Field, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from models.basemodel import EntityBaseModel
from models.enums import TicketStatus

if TYPE_CHECKING:
    from .lottery import Lottery
    from .prize import Prize


class Ticket(EntityBaseModel, table=True):
    __tablename__ = "ticket"

    status: TicketStatus = Field(default=TicketStatus.vacant)
    is_winner: bool = Field(default=False)
    purchase_date: Optional[datetime] = Field(default=None)
    price: int
    serial_number: str = Field(unique=True, index=True)

    lottery_id: UUID = Field(foreign_key="lottery.id")
    lottery: "Lottery" = Relationship(back_populates="tickets")

    user_id: Optional[UUID]

    prize: Optional["Prize"] = Relationship(back_populates="ticket", sa_relationship_kwargs={'uselist': False})