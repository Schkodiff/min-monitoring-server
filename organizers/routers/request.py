from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from config.database import get_session
from config.security import SecurityManager
from models.enums import UserRole
from responses.API_response import SuccessAPIResponse
from responses.factory import Factory
from schemas.request import RequestCreate, RequestStatusChange, RequestUpdate
from services.request_service import RequestService, get_request_service

router = APIRouter()


@router.get("/", response_model=SuccessAPIResponse)
def get_all_requests(
    session: Session = Depends(get_session),
    service: RequestService = Depends(get_request_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    return Factory.create_ok_reponse(data=service.get_all_requests(session))


@router.get("/by-user/{user_id}", response_model=SuccessAPIResponse)
def get_requests_by_user(
    user_id: UUID,
    session: Session = Depends(get_session),
    service: RequestService = Depends(get_request_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    return Factory.create_ok_reponse(data=service.get_by_user(session, user_id))


@router.get("/{request_id}", response_model=SuccessAPIResponse)
def get_request(
    request_id: UUID,
    session: Session = Depends(get_session),
    service: RequestService = Depends(get_request_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    return Factory.create_ok_reponse(data=service.get_request(session, request_id))


@router.post("/", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_create: RequestCreate,
    session: Session = Depends(get_session),
    service: RequestService = Depends(get_request_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    current_user_id, current_user_role = current_user
    return Factory.create_ok_reponse(
        data=service.create_request(
            session,
            request_create,
            current_user_id,
            current_user_role,
        )
    )


@router.patch("/{request_id}", response_model=SuccessAPIResponse)
def update_request(
    request_id: UUID,
    request_update: RequestUpdate,
    session: Session = Depends(get_session),
    service: RequestService = Depends(get_request_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    return Factory.create_ok_reponse(data=service.update_request(session, request_id, request_update))


@router.patch("/{request_id}/status", response_model=SuccessAPIResponse)
def change_request_status(
    request_id: UUID,
    status_change: RequestStatusChange,
    session: Session = Depends(get_session),
    service: RequestService = Depends(get_request_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    current_user_id, current_user_role = current_user
    return Factory.create_ok_reponse(
        data=service.change_request_status(
            session,
            request_id,
            status_change,
            current_user_id,
            current_user_role,
        )
    )


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: UUID,
    session: Session = Depends(get_session),
    service: RequestService = Depends(get_request_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    service.delete_request(session, request_id)
    return None
