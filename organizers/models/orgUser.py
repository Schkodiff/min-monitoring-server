from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID

if TYPE_CHECKING:
    from .organizer import Organizer


class OrgUsersLink(SQLModel, table=True):
    org_id: UUID = Field(foreign_key="organizer.id", primary_key=True)
    user_id: UUID = Field(primary_key=True, index=True)

    # user_id belongs to the users service, so this service stores only the UUID.
    organizer: "Organizer" = Relationship(back_populates="employees")
