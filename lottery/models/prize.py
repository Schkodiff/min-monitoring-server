from sqlmodel import Field, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING, Any, List, Optional
from uuid import UUID, uuid4

from models.basemodel import EntityBaseModel

if TYPE_CHECKING:
    from .lottery import Lottery
    from .ticket import Ticket

class Prize(EntityBaseModel, table=True):
    __tablename__ = "prize"


    name: str = Field(index=True)
    description: str
    img_path: str #List[]
    price: int

    lottery_id: UUID = Field(foreign_key="lottery.id")
    lottery: "Lottery" = Relationship(back_populates="prizes")

    ticket_id: Optional[UUID] = Field(foreign_key="ticket.id")
    ticket: Optional["Ticket"] = Relationship(back_populates="prize")