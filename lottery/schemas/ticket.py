from pydantic import field_validator, BaseModel
from typing import Any, List, Optional
from datetime import datetime
from uuid import UUID

from models.basemodel import EntityBaseModel
from models.enums import TicketStatus


class TicketResponse(EntityBaseModel):
    is_winner: bool
    purchase_date: Optional[datetime]
    price: int
    serial_number: str
    lottery_id: UUID
    status: TicketStatus

class TicketUserIdResponse(EntityBaseModel):
    user_id: Optional[UUID]


class TicketCreate(EntityBaseModel):
    is_winner: Optional[bool] = False
    price: int
    serial_number: str
    lottery_id: UUID


class TicketsBulkCreate(BaseModel):
    price: int
    lottery_id: UUID
    number: int

class TicketsRangeCreate(BaseModel):
    price: int
    lottery_id: UUID
    serial_number1: str
    serial_number2: str


class TicketUpdate(EntityBaseModel):
    is_winner: Optional[bool] = None
    price: Optional[int] = None
    status: Optional[TicketStatus] = None


class TicketStatusChange(EntityBaseModel):
    status: TicketStatus


class TicketPrizeConnect(BaseModel):
    prize_id: UUID


class BuyTicketsRequest(BaseModel):
    ticket_ids: List[UUID]
    user_id: UUID