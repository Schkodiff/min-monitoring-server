from typing import Optional, List
from uuid import UUID
from .base_repository import BaseRepository
from sqlmodel import Session, select

from models.user import User
from models.user import UserRole

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        return session.query(User).filter(User.email == email).first()

    def get_by_phone(self, session: Session, phone: str) -> Optional[User]:
        return session.query(User).filter(User.phone == phone).first()

    def update_password(self, session: Session, user: User, new_password: str) -> None:
        user.password = new_password
        session.add(user)
        session.commit()
        session.refresh(user)

    def change_role(self, session: Session, user: User, new_role: UserRole) -> None:
        user.role = new_role
        session.add(user)
        session.commit()
        session.refresh(user)

    def get_by_telegram_code(self, session: Session, telegram_code: str) -> Optional[User]:
        return session.query(User).filter(User.telegram_code == telegram_code).first()

    def get_by_telegram_id(self, session: Session, telegram_id: int) -> Optional[User]:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

    def set_telegram_code(self, session: Session, user: User, code: str) -> None:
        user.telegram_code = code
        session.add(user)
        session.commit()
        session.refresh(user)

    def link_telegram_id(self, session: Session, user: User, telegram_id: int) -> None:
        user.telegram_id = telegram_id
        session.add(user)
        session.commit()
        session.refresh(user)