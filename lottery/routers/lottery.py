from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from config.security import SecurityManager
from models.enums import UserRole
from sqlmodel import Session

from schemas.lottery import LotteryUpdate, LotteryResponse, LotteryCreate
from config.database import get_session
from services.lottery_service import LotteryService, get_lottery_service
from responses.factory import Factory
from responses.API_response import SuccessAPIResponse

router = APIRouter()


@router.get("/", response_model=SuccessAPIResponse)
def get_all_lotteries(session: Session = Depends(get_session), service: LotteryService = Depends(get_lottery_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_all_lotteries(session))


@router.get("/organizer/{org_id}", response_model=SuccessAPIResponse)
def get_lotteries_by_organizer(org_id: UUID, session: Session = Depends(get_session), service: LotteryService = Depends(get_lottery_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_lotteries_by_org(session, org_id))


@router.get("/{lottery_id}", response_model=SuccessAPIResponse)
def get_lottery(lottery_id: UUID, session: Session = Depends(get_session), service: LotteryService = Depends(get_lottery_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_lottery(session, lottery_id))


@router.post("/", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_lottery(lottery_create: LotteryCreate, session: Session = Depends(get_session), service: LotteryService = Depends(get_lottery_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    current_user_id, current_user_role = current_user
    if current_user_role != UserRole.organizer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только организаторы могут создавать розыгрыши")
    return Factory.create_ok_reponse(data=service.create_lottery(session, lottery_create))


@router.patch("/{lottery_id}", response_model=SuccessAPIResponse)
def update_lottery(lottery_id: UUID, lottery_update: LotteryUpdate, session: Session = Depends(get_session), service: LotteryService = Depends(get_lottery_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    current_user_id, current_user_role = current_user
    if current_user_role != UserRole.organizer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только организаторы могут обновлять розыгрыши")
    return Factory.create_ok_reponse(data=service.update_lottery(session, lottery_id, lottery_update))


@router.delete("/{lottery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lottery(lottery_id: UUID, session: Session = Depends(get_session), service: LotteryService = Depends(get_lottery_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    current_user_id, current_user_role = current_user
    if current_user_role != UserRole.organizer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только организаторы могут удалять розыгрыши")
    service.delete_lottery(session, lottery_id)
    return None

