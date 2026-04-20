import os
from pathlib import Path


def get_data_dir() -> Path:
    """Get data directory from environment variable or use default."""
    data_dir = os.getenv("KANBAN_DATA_DIR", "data")
    return Path(data_dir)


def get_data_file() -> Path:
    """Get the JSON data file path."""
    return get_data_dir() / "kanban.json"


def get_sqlite_file() -> Path:
    """Get SQLite file path from environment variable or use default."""
    sqlite_file = os.getenv("KANBAN_SQLITE_FILE", str(get_data_dir() / "kanban.db"))
    return Path(sqlite_file)


def get_database_url() -> str:
    """Get SQLAlchemy database URL, defaulting to SQLite."""
    return os.getenv("KANBAN_DATABASE_URL", f"sqlite:///{get_sqlite_file()}")


def get_storage_backend() -> str:
    """Get storage backend type (json/sqlite)."""
    return os.getenv("KANBAN_STORAGE_BACKEND", "sqlite").lower()