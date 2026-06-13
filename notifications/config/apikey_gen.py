import os
from uuid import uuid4

from sqlmodel import Session

from config.api_keys import ApiKeyTable


def generate_api_key() -> str:
    return str(uuid4())


def _configured_api_key() -> str | None:
    api_key = os.getenv("API_KEY")
    if api_key:
        return api_key

    if os.getenv("ENVIRONMENT", "").lower() in {"prod", "production"}:
        raise RuntimeError("API_KEY must be set in production")

    return None


def create_api_key(session: Session) -> str:
    configured_key = _configured_api_key()

    if configured_key:
        existing_key = session.query(ApiKeyTable).filter(ApiKeyTable.key == configured_key).first()
        if existing_key:
            if not existing_key.is_active:
                existing_key.is_active = True
                session.add(existing_key)
                session.commit()
                session.refresh(existing_key)
            return existing_key.key

    existing_active_key = session.query(ApiKeyTable).filter(ApiKeyTable.is_active == True).first()
    if existing_active_key:
        return existing_active_key.key

    key = configured_key or generate_api_key()
    db_key = ApiKeyTable(
        key=key,
        is_active=True,
        **({"scope": os.getenv("API_KEY_SCOPE")} if os.getenv("API_KEY_SCOPE") else {}),
    )
    session.add(db_key)
    session.commit()
    session.refresh(db_key)
    return key
