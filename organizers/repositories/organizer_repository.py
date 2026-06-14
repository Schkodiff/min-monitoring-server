from typing import Optional, List
from uuid import UUID
from .base_repository import BaseRepository
from pydantic import BaseModel
from sqlmodel import Session, select

from models.orgUser import OrgUsersLink
from models.organizer import Organizer


class OrganizerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Organizer)

    def create_with_owner(
        self,
        session: Session,
        obj: BaseModel,
        owner_user_id: UUID,
    ) -> Organizer:
        return self.create_from_dict_with_owner(
            session,
            obj.model_dump(),
            owner_user_id,
        )

    def create_from_dict_with_owner(
        self,
        session: Session,
        data: dict,
        owner_user_id: UUID,
    ) -> Organizer:
        organizer = Organizer(**data)
        owner_link = OrgUsersLink(org_id=organizer.id, user_id=owner_user_id)
        session.add(organizer)
        session.add(owner_link)
        session.commit()
        session.refresh(organizer)
        return organizer

    def get_by_email(self, session: Session, email: str) -> Optional[Organizer]:
        return session.query(Organizer).filter(Organizer.email == email).first()

    def get_by_phone(self, session: Session, phone: str) -> Optional[Organizer]:
        return session.query(Organizer).filter(Organizer.phone == phone).first()

    def get_by_address(self, session: Session, address: str) -> Optional[Organizer]:
        return session.query(Organizer).filter(Organizer.address == address).first()

    def get_by_inn(self, session: Session, inn: int) -> Optional[Organizer]:
        return session.query(Organizer).filter(Organizer.inn == inn).first()

    def get_by_ogrn(self, session: Session, ogrn: int) -> Optional[Organizer]:
        return session.query(Organizer).filter(Organizer.ogrn == ogrn).first()

    def delete(self, session: Session, id: UUID) -> None:
        owner_links = session.exec(
            select(OrgUsersLink).where(OrgUsersLink.org_id == id)
        ).all()
        for owner_link in owner_links:
            session.delete(owner_link)
        super().delete(session, id)

    def update_password(self, session: Session, organizer: Organizer, new_password: str) -> None:
        organizer.password = new_password
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

