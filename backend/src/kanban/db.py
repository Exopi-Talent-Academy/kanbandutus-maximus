from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import get_database_url

if "Base" not in globals():
    Base = declarative_base()

if "SessionLocal" not in globals():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False)

DATABASE_URL = ""
engine = None


def _configure_engine() -> None:
    global DATABASE_URL, engine

    DATABASE_URL = get_database_url()

    if DATABASE_URL.startswith("sqlite:///"):
        sqlite_path = DATABASE_URL.replace("sqlite:///", "", 1)
        if sqlite_path != ":memory:":
            Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    )
    SessionLocal.configure(bind=engine)


_configure_engine()


def ensure_db_engine() -> None:
    if get_database_url() != DATABASE_URL:
        _configure_engine()


def get_session():
    ensure_db_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    ensure_db_engine()
    from . import orm_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
