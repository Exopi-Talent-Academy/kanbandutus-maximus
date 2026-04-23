"""
Configuration for the Kanban application.

This module provides configuration for:
- Storage (backend type, data directory, database URL)
- CORS (allowed origins for cross-origin requests)

Environment Variables:
- KANBAN_STORAGE_BACKEND: "json" or "sqlite" (default: sqlite)
- KANBAN_DATA_DIR: Base directory for data files (default: data)
- KANBAN_DATABASE_URL: Full SQLAlchemy URL (deprecated, see docs/config.md)
- KANBAN_SQLITE_FILE: SQLite file path (deprecated, see docs/config.md)
- KANBAN_CORS_ORIGINS: Comma-separated list of allowed origins
"""

import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

STORAGE_BACKENDS = {"json", "sqlite"}


@dataclass
class StorageConfig:
    """Storage configuration with legacy fallback support.

    Attributes:
        backend: Storage backend type ("json" or "sqlite")
        data_dir: Base directory for data files
        database_url: Full SQLAlchemy URL (optional override)
        json_file: Path to JSON data file (computed)
        sqlite_url: SQLite database URL (computed)

    Example:
        >>> config = StorageConfig(backend="sqlite", data_dir=Path("data"))
        >>> config.sqlite_url
        'sqlite:///data/kanban.db'
    """

    backend: Literal["json", "sqlite"]
    data_dir: Path
    database_url: str | None = None
    _legacy_source: str | None = field(default=None, repr=False)

    @property
    def json_file(self) -> Path:
        """Path to JSON data file."""
        return self.data_dir / "kanban.json"

    @property
    def sqlite_url(self) -> str:
        """SQLite database URL."""
        if self.database_url:
            return self.database_url
        return f"sqlite:///{self.data_dir / 'kanban.db'}"


def _warn_deprecated(name: str) -> None:
    """Show deprecation warning for legacy environment variables."""
    warnings.warn(
        f"Environment variable '{name}' is deprecated. "
        f"Use 'KANBAN_DATA_DIR' and 'KANBAN_STORAGE_BACKEND' instead. "
        f"See docs/config.md for migration guide.",
        DeprecationWarning,
        stacklevel=3,
    )


def get_storage_config() -> StorageConfig:
    """Get storage configuration from environment variables.

    Primary configuration via:
    - KANBAN_STORAGE_BACKEND: "json" or "sqlite" (default: sqlite)
    - KANBAN_DATA_DIR: Base directory (default: data)

    Legacy fallbacks (with deprecation warnings):
    - KANBAN_DATABASE_URL: Full SQLAlchemy URL
    - KANBAN_SQLITE_FILE: SQLite file path

    Returns:
        StorageConfig with all storage settings

    Raises:
        ValueError: If KANBAN_STORAGE_BACKEND is invalid

    Example:
        >>> config = get_storage_config()
        >>> config.backend
        'sqlite'
    """
    data_dir = Path(os.getenv("KANBAN_DATA_DIR", "data"))
    backend = os.getenv("KANBAN_STORAGE_BACKEND", "sqlite").lower()

    if backend not in STORAGE_BACKENDS:
        raise ValueError(
            f"Invalid KANBAN_STORAGE_BACKEND: '{backend}'. "
            f"Must be one of: {', '.join(STORAGE_BACKENDS)}"
        )

    # Check for legacy environment variables
    if db_url := os.getenv("KANBAN_DATABASE_URL"):
        _warn_deprecated("KANBAN_DATABASE_URL")
        return StorageConfig(
            backend=backend,  # type: ignore[literal-required]
            data_dir=data_dir,
            database_url=db_url,
            _legacy_source="KANBAN_DATABASE_URL",
        )

    if sqlite_file := os.getenv("KANBAN_SQLITE_FILE"):
        _warn_deprecated("KANBAN_SQLITE_FILE")
        return StorageConfig(
            backend=backend,  # type: ignore[literal-required]
            data_dir=data_dir,
            database_url=f"sqlite:///{sqlite_file}",
            _legacy_source="KANBAN_SQLITE_FILE",
        )

    return StorageConfig(backend=backend, data_dir=data_dir)  # type: ignore[literal-required]


# =============================================================================
# Legacy Functions (Deprecated)
# =============================================================================


def get_data_dir() -> Path:
    """Get data directory from environment variable or use default.

    .. deprecated::
        Use :func:`get_storage_config` instead.

    Returns:
        Path to the data directory

    Example:
        >>> path = get_data_dir()  # doctest: +SKIP
        PosixPath('data')
    """
    warnings.warn(
        "get_data_dir() is deprecated. "
        "Use get_storage_config().data_dir instead. "
        "See docs/config.md for migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_storage_config().data_dir


def get_data_file() -> Path:
    """Get the JSON data file path.

    .. deprecated::
        Use :func:`get_storage_config` instead.

    Returns:
        Path to the JSON data file

    Example:
        >>> path = get_data_file()  # doctest: +SKIP
        PosixPath('data/kanban.json')
    """
    warnings.warn(
        "get_data_file() is deprecated. "
        "Use get_storage_config().json_file instead. "
        "See docs/config.md for migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_storage_config().json_file


def get_sqlite_file() -> Path:
    """Get SQLite file path from environment variable or use default.

    .. deprecated::
        Use :func:`get_storage_config` instead.

    Returns:
        Path to the SQLite database file

    Example:
        >>> path = get_sqlite_file()  # doctest: +SKIP
        PosixPath('data/kanban.db')
    """
    warnings.warn(
        "get_sqlite_file() is deprecated. "
        "Use get_storage_config().sqlite_url instead. "
        "See docs/config.md for migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    config = get_storage_config()
    if config.database_url and config.database_url.startswith("sqlite:///"):
        return Path(config.database_url.replace("sqlite:///", "", 1))
    return config.data_dir / "kanban.db"


def get_database_url() -> str:
    """Get SQLAlchemy database URL, defaulting to SQLite.

    .. deprecated::
        Use :func:`get_storage_config` instead.

    Returns:
        SQLAlchemy database URL

    Example:
        >>> url = get_database_url()  # doctest: +SKIP
        'sqlite:///data/kanban.db'
    """
    warnings.warn(
        "get_database_url() is deprecated. "
        "Use get_storage_config().sqlite_url instead. "
        "See docs/config.md for migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_storage_config().sqlite_url


def get_storage_backend() -> str:
    """Get storage backend type (json/sqlite).

    .. deprecated::
        Use :func:`get_storage_config` instead.

    Returns:
        Storage backend type

    Example:
        >>> backend = get_storage_backend()  # doctest: +SKIP
        'sqlite'
    """
    warnings.warn(
        "get_storage_backend() is deprecated. "
        "Use get_storage_config().backend instead. "
        "See docs/config.md for migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_storage_config().backend


# =============================================================================
# CORS Configuration
# =============================================================================

# CORS (Cross-Origin Resource Sharing) configuration
# Add frontend origins that should be allowed to access the API.
# Common development ports:
#   - 4200: Angular default
#   - 3000: React/Vue default, also common for staging
# Remove or modify these for production deployment.
DEFAULT_CORS_ORIGINS = [
    "http://localhost:4200",  # Angular dev server
    "http://localhost:3000",  # React/Vue dev server
    "http://example.com:3000",  # Example staging/production
]


def get_cors_origins() -> list[str]:
    """Get allowed CORS origins from config or environment.

    Returns:
        List of allowed origin URLs

    Example:
        >>> origins = get_cors_origins()  # doctest: +SKIP
        ['http://localhost:4200', 'http://localhost:3000']
    """
    env_origins = os.getenv("KANBAN_CORS_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return DEFAULT_CORS_ORIGINS
