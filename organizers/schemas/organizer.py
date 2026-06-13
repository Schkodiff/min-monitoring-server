from pydantic import field_validator
from typing import Any, List, Optional
from datetime import datetime
from uuid import UUID

from models.basemodel import EntityBaseModel
from models.orgUser import OrgUsersLink


class OrganizerResponse(EntityBaseModel):
    name: str
    inn: int
    ogrn: int
    phone: str
    address: str
    logo: Optional[str] = None
    email: str
    description: Optional[str] = None
    employees: List["OrgUsersLink"]


class OrganizerCreate(EntityBaseModel):
    name: str
    inn: int
    ogrn: int
    phone: str
    address: str
    logo: Optional[str] = None
    email: str
    description: Optional[str] = None


class OrganizerUpdate(EntityBaseModel):
    name: Optional[str] = None
    inn: Optional[int] = None
    ogrn: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None