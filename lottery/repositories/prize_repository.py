from typing import Optional, List
from uuid import UUID
from .base_repository import BaseRepository
from sqlmodel import Session, select

from models.prize import Prize


class PrizeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Prize)

    def get_by_lottery_id(self, session: Session, lottery_id: UUID) -> List[Prize]:
        return session.query(Prize).filter(Prize.lottery_id == lottery_id).all()

    def get_by_name(self, session: Session, name: str) -> Optional[Prize]:
        return session.query(Prize).filter(Prize.name == name).first()

