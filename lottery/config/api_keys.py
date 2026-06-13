from enum import Enum
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class ApiKeyScope(str, Enum):
    FRONTEND = "frontend"
    TG_BOT = "tg_bot"


class ApiKeyTable(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    key: str = Field(unique=True)
    is_active: bool = Field(default=True)
    scope: ApiKeyScope = Field(default=ApiKeyScope.FRONTEND)