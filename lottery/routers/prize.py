from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from schemas.prize import PrizeUpdate, PrizeResponse, PrizeCreate
from config.database import get_session
from services.prize_service import PrizeService, get_prize_service
from responses.factory import Factory
from responses.API_response import SuccessAPIResponse
from config.security import SecurityManager
from models.enums import UserRole

router = APIRouter()


@router.get("/", response_model=SuccessAPIResponse)
def get_all_prizes(session: Session = Depends(get_session), service: PrizeService = Depends(get_prize_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_all_prizes(session))


@router.get("/{prize_id}", response_model=SuccessAPIResponse)
def get_prize(prize_id: UUID, session: Session = Depends(get_session), service: PrizeService = Depends(get_prize_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_prize(session, prize_id))


@router.get("/lottery/{lottery_id}", response_model=SuccessAPIResponse)
def get_prizes_by_lottery(lottery_id: UUID, session: Session = Depends(get_session), service: PrizeService = Depends(get_prize_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_prizes_by_lottery(session, lottery_id))


@router.post("/", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_prize(prize_create: PrizeCreate, session: Session = Depends(get_session), service: PrizeService = Depends(get_prize_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.create_prize(session, prize_create))


@router.patch("/{prize_id}", response_model=SuccessAPIResponse)
def update_prize(prize_id: UUID, prize_update: PrizeUpdate, session: Session = Depends(get_session), service: PrizeService = Depends(get_prize_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.update_prize(session, prize_id, prize_update))


@router.delete("/{prize_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prize(prize_id: UUID, session: Session = Depends(get_session), service: PrizeService = Depends(get_prize_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    service.delete_prize(session, prize_id)
    return None

