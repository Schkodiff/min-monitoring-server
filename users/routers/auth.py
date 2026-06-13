from fastapi import APIRouter, Depends, status, Request, HTTPException, Response
from sqlmodel import Session
from uuid import UUID

from models.user import UserRole
from schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, SetPasswordRequest
from schemas.user import UserCreate
from config.database import get_session
from config.security import SecurityManager
from services.auth_service import AuthService, get_auth_service
from responses.API_response import SuccessAPIResponse
from responses.factory import Factory


router = APIRouter()


@router.post("/register", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def register(response: Response, payload: UserCreate, session: Session = Depends(get_session), service: AuthService = Depends(get_auth_service)):
    data=service.register(response, session, payload)
    return Factory.create_ok_reponse(data)

@router.post("/login", response_model=SuccessAPIResponse)
def login(response: Response, payload: LoginRequest, session: Session = Depends(get_session), service: AuthService = Depends(get_auth_service)):
    data=service.login(response, session, payload)
    return Factory.create_ok_reponse(data)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token), service: AuthService = Depends(get_auth_service)):
    current_user_id, current_user_role = current_user
    service.logout(response, current_user_id)
    return None

@router.post("/refresh-token", response_model=SuccessAPIResponse)
def refresh_token(response: Response, payload: RefreshTokenRequest, request: Request, session: Session = Depends(get_session), service: AuthService = Depends(get_auth_service)):
    refresh_token_value = payload.refresh_token or request.cookies.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    data=service.refresh(response, session, refresh_token_value)
    return Factory.create_ok_reponse(data)

@router.post("/set-password", status_code=status.HTTP_204_NO_CONTENT)
# @login_required
def set_password(payload: SetPasswordRequest, current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token), session: Session = Depends(get_session), service: AuthService = Depends(get_auth_service)):
    current_user_id, current_user_role = current_user
    service.set_password(session, current_user_id, payload)
    return None