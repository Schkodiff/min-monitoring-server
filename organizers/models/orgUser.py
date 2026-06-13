from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID

if TYPE_CHECKING:
    from .organizer import Organizer


class OrgUsersLink(SQLModel, table=True):
    #org_id: UUID = Field(default_factory=uuid4, primary_key=True) #relationship backpopulate
    #user_id: UUID = Field(default_factory=uuid4, primary_key=True)

    org_id: UUID = Field(foreign_key="organizer.id", primary_key=True)
    user_id: UUID = Field(primary_key=True)

    # Relationship back to Organizer, exposing employees on Organizer
    organizer: "Organizer" = Relationship(back_populates="employees")