import os

from passlib.hash import pbkdf2_sha256
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError

from models.user import UserRole
from config.api_keys import ApiKeyTable, ApiKeyScope
from config.apikey_handle import get_current_api_key


DEFAULT_JWT_SECRET_KEY = "your-secret-key-change-this-in-production"


def get_jwt_secret_key() -> str:
    secret_key = os.getenv("JWT_SECRET_KEY", DEFAULT_JWT_SECRET_KEY)
    if (
        os.getenv("ENVIRONMENT", "").lower() in {"prod", "production"}
        and secret_key == DEFAULT_JWT_SECRET_KEY
    ):
        raise RuntimeError("JWT_SECRET_KEY must be set in production")
    return secret_key


class SecurityManager:
    # Configuration
    SECRET_KEY = get_jwt_secret_key()
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60
    
    # Password hashing configuration
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Security scheme
    security = HTTPBearer(auto_error=False) #might need to change later
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pbkdf2_sha256.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return pbkdf2_sha256.verify(password, hashed)
    
    @classmethod
    def create_access_token(cls, user_id: UUID, user_role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode = {"sub": str(user_id), "exp": expire, "role": user_role.value}
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def decode_access_token(cls, request: Request, api_key: ApiKeyTable = Depends(get_current_api_key), credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), user_tg_id: Optional[UUID] = Header(None, alias="X-User-ID")) -> tuple[UUID, UserRole] | None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if api_key.scope.value == ApiKeyScope.TG_BOT.value:
            return user_tg_id, UserRole.participant
            #bot returns user_id 
        token: Optional[str] = None
        if credentials and credentials.credentials:
            token = credentials.credentials
        else:
            token = request.cookies.get("access_token")
        if not token:
            raise credentials_exception

        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            role: str = payload.get("role")
            
            if user_id is None or role is None:
                raise credentials_exception
            
            if token_type == "refresh":
                raise credentials_exception
            
            return UUID(user_id), UserRole(role)
        
        except InvalidTokenError:
            raise credentials_exception
        except ValueError:
            raise credentials_exception
    
    @classmethod
    def create_refresh_token(cls, user_id: UUID, user_role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=cls.REFRESH_TOKEN_EXPIRE_MINUTES))
        to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh", "role": user_role.value}
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def decode_refresh_token(cls, token: str) -> tuple[UUID, UserRole]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            role: str = payload.get("role")
            
            if user_id is None or role is None:
                raise credentials_exception
            
            if token_type != "refresh":
                raise credentials_exception
            
            return UUID(user_id), UserRole(role)
        
        except InvalidTokenError:
            raise credentials_exception
        except ValueError:
            raise credentials_exception
