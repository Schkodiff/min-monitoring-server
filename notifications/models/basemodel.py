from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class EntityBaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)