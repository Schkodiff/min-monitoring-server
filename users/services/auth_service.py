from uuid import UUID
from fastapi import HTTPException, status, Response

from repositories.user_repository import UserRepository
from schemas.auth import LoginRequest, TokenResponse, SetPasswordRequest
from schemas.user import UserCreate
from config.security import SecurityManager


def set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    response.set_cookie(
        key="access_token",
        value=tokens.token,
        httponly=True,
        secure=False,  # change to True in production (HTTPS)
        samesite="lax",
        max_age=SecurityManager.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,  # change to True in production (HTTPS)
        samesite="lax",
        max_age=SecurityManager.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, response: Response, session, payload: UserCreate) -> TokenResponse:
        if self.users.get_by_email(session, payload.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Электронная почта уже зарегистрирована")
        if self.users.get_by_phone(session, payload.phone):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Номер телефона уже зарегистрирован")

        hashed_password = SecurityManager.hash_password(payload.password)
        payload_dict = payload.model_dump()
        payload_dict['password'] = hashed_password
        user = self.users.create(session, UserCreate(**payload_dict))
        access_token = SecurityManager.create_access_token(user_id=user.id, user_role=user.role)
        refresh_token = SecurityManager.create_refresh_token(user_id=user.id, user_role=user.role)
        tokens = TokenResponse(token=access_token, refresh_token=refresh_token)
        set_auth_cookies(response, tokens)
        return tokens

    def login(self, response: Response, session, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(session, payload.email)
        if not user or not SecurityManager.verify_password(payload.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access_token = SecurityManager.create_access_token(user_id=user.id, user_role=user.role)
        refresh_token = SecurityManager.create_refresh_token(user_id=user.id, user_role=user.role)
        tokens = TokenResponse(token=access_token, refresh_token=refresh_token)
        set_auth_cookies(response, tokens)
        return tokens

    def logout(self, response: Response, user_id: UUID) -> None:
        # Clear auth cookies for browser clients
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

    def refresh(self, response: Response, session, refresh_token: str) -> TokenResponse:
        user_id, user_role = SecurityManager.decode_refresh_token(refresh_token)
        user = self.users.get(session, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        access_token = SecurityManager.create_access_token(user_id=user_id, user_role=user_role)
        new_refresh_token = SecurityManager.create_refresh_token(user_id=user_id, user_role=user_role)
        tokens = TokenResponse(token=access_token, refresh_token=new_refresh_token)
        set_auth_cookies(response, tokens)
        return tokens

    def set_password(self, session, user_id: UUID, payload: SetPasswordRequest) -> None:
        user = self.users.get(session, user_id)
        if not user or not SecurityManager.verify_password(payload.old_password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        self.users.update_password(session, user, SecurityManager.hash_password(payload.new_password))


def get_auth_service():
    return AuthService(UserRepository())
