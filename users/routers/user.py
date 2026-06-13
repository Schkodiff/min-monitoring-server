from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session
from typing import List, Optional

from schemas.user import UserLinkTelegram, UserUpdate, UserResponse, UserChangeRole
from config.database import get_session
from config.security import SecurityManager
from config.api_keys import ApiKeyTable
from config.apikey_handle import get_current_api_key
from services.user_service import UserService, get_user_service
from responses.factory import Factory
from models.user import UserRole
from responses.API_response import SuccessAPIResponse

router = APIRouter()


@router.get("/", response_model=SuccessAPIResponse)
def get_all_users(session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_all_users(session))

@router.get("/{user_id}", response_model=SuccessAPIResponse)
def get_user(user_id: UUID, session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_user(session, user_id))


@router.patch("/{user_id}", response_model=SuccessAPIResponse)
def update_user(
    user_id: UUID, user_update: UserUpdate, session: Session = Depends(get_session), service: UserService = Depends(get_user_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)): #, api_key: ApiKeyTable = Depends(get_current_api_key)):
    current_user_id, current_user_role = current_user
    return Factory.create_ok_reponse(data=service.update_user(session, user_id, user_update, current_user_id))


@router.patch("/{user_id}/role", response_model=SuccessAPIResponse)
def change_role(user_id: UUID, user_change_role: UserChangeRole, session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    current_user_id, current_user_role = current_user
    return Factory.create_ok_reponse(data=service.change_role(session, user_id, user_change_role, current_user_role))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    current_user_id, current_user_role = current_user
    service.delete_user(session, user_id, current_user_id)
    return None


@router.patch("/{user_id}/gen-telegram-code", response_model=SuccessAPIResponse)
def generate_telegram_code(session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    current_user_id, current_user_role = current_user
    data = service.generate_telegram_code(session, current_user_id)
    return Factory.create_ok_reponse(data=data)


@router.post("/link-telegram-id", response_model=SuccessAPIResponse)
def link_telegram_id(user_link_telegram: UserLinkTelegram, session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    data = service.link_telegram_id(session, user_link_telegram.telegram_id, user_link_telegram.telegram_code)
    return Factory.create_ok_reponse(data=data)

@router.get("/{user_id}/telegram-id", response_model=SuccessAPIResponse)
def get_telegram_id(user_id: UUID, session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    data = service.get_telegram_id(session, user_id)
    return Factory.create_ok_reponse(data=data)

@router.get("/telegram/{telegram_id}/user-id", response_model=SuccessAPIResponse)
def get_user_id_by_telegram_id(telegram_id: int, session: Session = Depends(get_session), service: UserService = Depends(get_user_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    data = service.get_user_id_by_telegram_id(session, telegram_id)
    return Factory.create_ok_reponse(data=data)
