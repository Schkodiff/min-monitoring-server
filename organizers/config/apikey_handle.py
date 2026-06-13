from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlmodel import select, Session

from config.database import get_session
from config.api_keys import ApiKeyTable

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_current_api_key(
    session: Session = Depends(get_session),
    x_api_key: str = Depends(api_key_header),) -> ApiKeyTable:
    if not x_api_key:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    api_key_row = session.query(ApiKeyTable).filter(ApiKeyTable.key == x_api_key, ApiKeyTable.is_active == True).first()

    if not api_key_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return api_key_row