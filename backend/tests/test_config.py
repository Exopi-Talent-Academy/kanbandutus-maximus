# ============================================================================
# Configuration Tests
# ============================================================================
# Tests for storage configuration, including deprecation warnings for legacy
# environment variables.
# ============================================================================

import warnings

import pytest


def test_get_storage_config_default(monkeypatch):
    """Test that default configuration works without warnings."""
    monkeypatch.delenv("KANBAN_DATA_DIR", raising=False)
    monkeypatch.delenv("KANBAN_STORAGE_BACKEND", raising=False)
    monkeypatch.delenv("KANBAN_DATABASE_URL", raising=False)
    monkeypatch.delenv("KANBAN_SQLITE_FILE", raising=False)

    from src.kanban.config import get_storage_config

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        config = get_storage_config()

        assert config.backend == "sqlite"
        assert str(config.data_dir) == "data"
        assert config.database_url is None

        deprecation_warnings = [
            x for x in w if issubclass(x.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) == 0


def test_get_storage_config_json_backend(monkeypatch):
    """Test JSON backend configuration without warnings."""
    monkeypatch.setenv("KANBAN_STORAGE_BACKEND", "json")
    monkeypatch.setenv("KANBAN_DATA_DIR", "/custom/data")

    from src.kanban.config import get_storage_config

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        config = get_storage_config()

        assert config.backend == "json"
        assert str(config.data_dir) == "/custom/data"
        assert str(config.json_file) == "/custom/data/kanban.json"

        deprecation_warnings = [
            x for x in w if issubclass(x.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) == 0


def test_get_storage_config_sqlite_backend(monkeypatch):
    """Test SQLite backend configuration without warnings."""
    monkeypatch.setenv("KANBAN_STORAGE_BACKEND", "sqlite")
    monkeypatch.setenv("KANBAN_DATA_DIR", "/var/lib/kanban")

    from src.kanban.config import get_storage_config

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        config = get_storage_config()

        assert config.backend == "sqlite"
        assert str(config.data_dir) == "/var/lib/kanban"
        assert config.sqlite_url == "sqlite:////var/lib/kanban/kanban.db"

        deprecation_warnings = [
            x for x in w if issubclass(x.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) == 0


def test_get_storage_config_invalid_backend(monkeypatch):
    """Test that invalid backend raises ValueError."""
    monkeypatch.setenv("KANBAN_STORAGE_BACKEND", "invalid")

    from src.kanban.config import get_storage_config

    with pytest.raises(ValueError) as exc_info:
        get_storage_config()

    assert "Invalid KANBAN_STORAGE_BACKEND" in str(exc_info.value)


def test_get_storage_config_warns_on_database_url(monkeypatch):
    """Test that KANBAN_DATABASE_URL triggers deprecation warning."""
    monkeypatch.setenv("KANBAN_DATABASE_URL", "postgresql://localhost/test")

    from src.kanban.config import get_storage_config

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        config = get_storage_config()

        assert config.database_url == "postgresql://localhost/test"

        deprecation_warnings = [
            x for x in w if issubclass(x.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) == 1
        assert "KANBAN_DATABASE_URL" in str(deprecation_warnings[0].message)
        assert "deprecated" in str(deprecation_warnings[0].message).lower()
        assert "docs/config.md" in str(deprecation_warnings[0].message)


def test_get_storage_config_warns_on_sqlite_file(monkeypatch):
    """Test that KANBAN_SQLITE_FILE triggers deprecation warning."""
    monkeypatch.setenv("KANBAN_SQLITE_FILE", "/custom/custom.db")

    from src.kanban.config import get_storage_config

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        config = get_storage_config()

        assert config.database_url == "sqlite:////custom/custom.db"

        deprecation_warnings = [
            x for x in w if issubclass(x.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) == 1
        assert "KANBAN_SQLITE_FILE" in str(deprecation_warnings[0].message)
        assert "deprecated" in str(deprecation_warnings[0].message).lower()
        assert "docs/config.md" in str(deprecation_warnings[0].message)


def test_legacy_get_data_dir_shows_warning():
    """Test that legacy get_data_dir() shows deprecation warning."""
    from src.kanban.config import get_data_dir

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = get_data_dir()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_data_dir" in str(w[0].message)
        assert "deprecated" in str(w[0].message).lower()
        assert "docs/config.md" in str(w[0].message)


def test_legacy_get_data_file_shows_warning():
    """Test that legacy get_data_file() shows deprecation warning."""
    from src.kanban.config import get_data_file

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = get_data_file()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_data_file" in str(w[0].message)
        assert "deprecated" in str(w[0].message).lower()


def test_legacy_get_sqlite_file_shows_warning():
    """Test that legacy get_sqlite_file() shows deprecation warning."""
    from src.kanban.config import get_sqlite_file

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = get_sqlite_file()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_sqlite_file" in str(w[0].message)
        assert "deprecated" in str(w[0].message).lower()


def test_legacy_get_database_url_shows_warning():
    """Test that legacy get_database_url() shows deprecation warning."""
    from src.kanban.config import get_database_url

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = get_database_url()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_database_url" in str(w[0].message)
        assert "deprecated" in str(w[0].message).lower()


def test_legacy_get_storage_backend_shows_warning():
    """Test that legacy get_storage_backend() shows deprecation warning."""
    from src.kanban.config import get_storage_backend

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = get_storage_backend()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_storage_backend" in str(w[0].message)
        assert "deprecated" in str(w[0].message).lower()


def test_storage_config_properties():
    """Test StorageConfig computed properties."""
    from pathlib import Path

    from src.kanban.config import StorageConfig

    config = StorageConfig(backend="sqlite", data_dir=Path("/data"))

    assert config.json_file == Path("/data/kanban.json")
    assert config.sqlite_url == "sqlite:////data/kanban.db"

    config_with_url = StorageConfig(
        backend="sqlite",
        data_dir=Path("/data"),
        database_url="sqlite:////var/lib/custom.db",
    )

    assert config_with_url.json_file == Path("/data/kanban.json")
    assert config_with_url.sqlite_url == "sqlite:////var/lib/custom.db"


def test_get_cors_origins_default():
    """Test that default CORS origins are returned."""
    from src.kanban.config import get_cors_origins

    origins = get_cors_origins()
    assert "http://localhost:4200" in origins
    assert "http://localhost:3000" in origins


def test_get_cors_origins_from_env(monkeypatch):
    """Test that CORS origins can be set via environment variable."""
    monkeypatch.setenv("KANBAN_CORS_ORIGINS", "http://example.com, http://test.com")

    from src.kanban.config import get_cors_origins

    origins = get_cors_origins()
    assert origins == ["http://example.com", "http://test.com"]
