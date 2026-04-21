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


# CORS (Cross-Origin Resource Sharing) configuration
# Add frontend origins that should be allowed to access the API.
# Common development ports:
#   - 4200: Angular default
#   - 3000: React/Vue default, also common for staging
# Remove or modify these for production deployment.
DEFAULT_CORS_ORIGINS = [
    "http://localhost:4200",   # Angular dev server
    "http://localhost:3000",   # React/Vue dev server
    "http://example.com:3000", # Example staging/production
]


def get_cors_origins() -> list[str]:
    """Get allowed CORS origins from config or environment."""
    env_origins = os.getenv("KANBAN_CORS_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return DEFAULT_CORS_ORIGINS