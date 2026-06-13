from typing import Optional, List
from uuid import UUID
from .base_repository import BaseRepository
from sqlmodel import Session, select

from models.enums import RequestStatus
from models.request import Request


class RequestRepository(BaseRepository):
    def __init__(self):
        super().__init__(Request)

    def get_by_user_id(self, session: Session, user_id: UUID) -> List[Request]:
        return (
            session.query(Request)
            .filter(Request.user_id == user_id)
            .order_by(Request.created_at.desc())
            .all()
        )
    def get_by_email(self, session: Session, email: str) -> Optional[Request]:
        return session.query(Request).filter(Request.email == email).first()

    def get_by_phone(self, session: Session, phone: str) -> Optional[Request]:
        return session.query(Request).filter(Request.phone == phone).first()

    def get_by_inn(self, session: Session, inn: int) -> Optional[Request]:
        return session.query(Request).filter(Request.inn == inn).first()

    def get_by_ogrn(self, session: Session, ogrn: int) -> Optional[Request]:
        return session.query(Request).filter(Request.ogrn == ogrn).first()

    def change_status(
        self,
        session: Session,
        request: Request,
        status: RequestStatus,
        poc_id: UUID,
        rejection_reason: Optional[str] = None,
    ) -> Request:
        request.status = status
        request.poc_id = poc_id
        if rejection_reason is not None:
            request.rejection_reason = rejection_reason
        session.add(request)
        session.commit()
        session.refresh(request)
        return request
