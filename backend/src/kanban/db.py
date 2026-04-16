from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import get_database_url

DATABASE_URL = get_database_url()

if DATABASE_URL.startswith("sqlite:///"):
    sqlite_path = DATABASE_URL.replace("sqlite:///", "", 1)
    from pathlib import Path

    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)

# check_same_thread is required for SQLite when used across FastAPI request handling.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import orm_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
