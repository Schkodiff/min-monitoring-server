from pydantic import BaseModel, field_validator
from typing import Any, List, Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel

from models.enums import RequestStatus
from models.basemodel import EntityBaseModel


class RequestResponse(EntityBaseModel):
    name: str
    inn: int
    ogrn: int
    phone: str
    address: str
    email: str
    logo: Optional[str] = None
    status: RequestStatus
    rejection_reason: Optional[str] = None

class RequestCreate(BaseModel):
    name: str
    inn: int
    ogrn: int
    phone: str
    address: str
    email: str
    logo: Optional[str] = None

class RequestUpdate(BaseModel):
    name: Optional[str] = None
    inn: Optional[int] = None
    ogrn: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    email: Optional[str] = None


class RequestStatusChange(BaseModel):
    status: RequestStatus
    rejection_reason: Optional[str] = None
