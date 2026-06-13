from typing import Optional, List
from uuid import UUID
from .base_repository import BaseRepository
from sqlmodel import Session, select

from models.organizer import Organizer


class OrganizerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Organizer)

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

    def update_password(self, session: Session, organizer: Organizer, new_password: str) -> None:
        organizer.password = new_password
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

