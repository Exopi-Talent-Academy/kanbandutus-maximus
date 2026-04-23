# ADR 011: Storage Configuration Consolidation

### Status
Accepted

### Decision
Consolidate storage configuration into a single `StorageConfig` dataclass with a unified `get_storage_config()` API.

### Goal
Eliminate multiple overlapping configuration paths (4 env vars → 2 storage locations) and provide a clean, typed configuration interface.

### Context
Current config.py has multiple functions with overlapping concerns:
- `get_data_dir()`, `get_data_file()` → JSON storage
- `get_sqlite_file()`, `get_database_url()` → SQLite storage
- `get_storage_backend()` → selects between them

This creates confusion about precedence and makes it hard to understand which env vars affect what.

### Decision
Replace with a single `StorageConfig` dataclass:

```python
@dataclass
class StorageConfig:
    backend: Literal["json", "sqlite"]
    data_dir: Path
    database_url: str | None  # Optional override
```

With `get_storage_config() -> StorageConfig` as the single entry point.

### Legacy Fallbacks
- `KANBAN_DATABASE_URL` → Sets `database_url` directly (with deprecation warning)
- `KANBAN_SQLITE_FILE` → Derives `database_url` (with deprecation warning)
- `KANBAN_DATA_DIR` → Sets `data_dir` (still supported)
- `KANBAN_STORAGE_BACKEND` → Sets `backend` (still supported)

### Migration Path
1. Users can continue using legacy env vars (deprecation warnings shown)
2. Recommended: Use `KANBAN_DATA_DIR` + `KANBAN_STORAGE_BACKEND`
3. Custom DB: Set `KANBAN_DATABASE_URL` (with warning)

### Alternatives Considered
- **Module-level constants**: Simpler but harder to test
- **Pydantic Settings**: More complex, adds dependency

### Trade-offs
**Pros:**
- Single source of truth
- Type-safe
- Clear migration path
- Backward compatible

**Cons:**
- Breaking change for code using old functions
- Deprecation warnings may clutter logs initially