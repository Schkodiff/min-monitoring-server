from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List

from repositories.prize_repository import PrizeRepository
from schemas.prize import PrizeUpdate, PrizeResponse, PrizeCreate


class PrizeService:
    def __init__(self, prizes: PrizeRepository):
        self.prizes = prizes

    def get_all_prizes(self, session: Session) -> List[PrizeResponse]:
        prizes = self.prizes.list_all(session)
        return [PrizeResponse.model_validate(prize) for prize in prizes]

    def get_prize(self, session: Session, prize_id: UUID) -> PrizeResponse:
        prize = self.prizes.get(session, prize_id)
        if not prize:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Приз не найден"
            )
        return PrizeResponse.model_validate(prize)

    def get_prizes_by_lottery(self, session: Session, lottery_id: UUID) -> List[PrizeResponse]:
        prizes = self.prizes.get_by_lottery_id(session, lottery_id)
        return [PrizeResponse.model_validate(prize) for prize in prizes]

    def create_prize(self, session: Session, prize_create: PrizeCreate) -> PrizeResponse:
        new_prize = self.prizes.create(session, prize_create)
        return PrizeResponse.model_validate(new_prize)

    def update_prize(self, session: Session, prize_id: UUID, prize_update: PrizeUpdate) -> PrizeResponse:
        prize = self.prizes.get(session, prize_id)
        if not prize:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Приз не найден"
            )
        
        updated_prize = self.prizes.update(session, prize_id, prize_update)
        return PrizeResponse.model_validate(updated_prize)

    def delete_prize(self, session: Session, prize_id: UUID) -> None:
        prize = self.prizes.get(session, prize_id)
        if not prize:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Приз не найден"
            )
        
        self.prizes.delete(session, prize_id)


def get_prize_service():
    return PrizeService(PrizeRepository())

