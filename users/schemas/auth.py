from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    token: str
    refresh_token: str



class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class SetPasswordRequest(BaseModel):
    old_password: str
    new_password: str