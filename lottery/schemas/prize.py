from pydantic import field_validator
from typing import Any, List, Optional
from uuid import UUID

from models.basemodel import EntityBaseModel


class PrizeResponse(EntityBaseModel):
    name: str
    description: str
    img_path: str
    price: int
    lottery_id: UUID


class PrizeCreate(EntityBaseModel):
    name: str
    description: str
    img_path: str
    price: int
    lottery_id: Optional[UUID] = None


class PrizeUpdate(EntityBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    img_path: Optional[str] = None
    price: Optional[int] = None
