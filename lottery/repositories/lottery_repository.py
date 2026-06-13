from typing import Optional, List
from uuid import UUID
from .base_repository import BaseRepository
from sqlmodel import Session, select

from models.lottery import Lottery


class LotteryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Lottery)

    def get_by_org_id(self, session: Session, org_id: UUID) -> List[Lottery]:
        return session.query(Lottery).filter(Lottery.org_id == org_id).all()

    def get_by_name(self, session: Session, name: str) -> Optional[Lottery]:
        return session.query(Lottery).filter(Lottery.name == name).first()

