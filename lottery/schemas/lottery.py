from pydantic import field_validator
from typing import Any, List, Optional, Dict
from datetime import datetime
from uuid import UUID

from models.basemodel import EntityBaseModel
from models.enums import LotteryStatus
from schemas.prize import PrizeCreate


class LotteryResponse(EntityBaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_entries: int
    org_id: UUID
    status: LotteryStatus
    randomizer_result: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class LotteryCreate(EntityBaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_entries: int
    org_id: UUID
    prizes: Optional[List[PrizeCreate]] = None
    description: Optional[str] = None


class LotteryUpdate(EntityBaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_entries: Optional[int] = None
    status: Optional[LotteryStatus] = None
    randomizer_result: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
