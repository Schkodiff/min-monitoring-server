import os
from pathlib import Path
from typing import Generator

from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker

from config.apikey_gen import create_api_key

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return

    sqlite_path = database_url.replace("sqlite:///", "", 1)
    if not sqlite_path or sqlite_path == ":memory:":
        return

    db_path = Path(sqlite_path)
    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent_dir(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=SQL_ECHO)
SessionLocal = sessionmaker(bind=engine)


def seed_api_key() -> None:
    with SessionLocal() as session:
        create_api_key(session)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
