# Storage Configuration

## Overview

The Kanban backend supports two storage backends:

| Backend | Storage Location | Use Case |
|---------|-----------------|----------|
| **JSON** | `data/kanban.json` | Development, simple deployments |
| **SQLite** | `data/kanban.db` | Production, recommended |

## Environment Variables

### Modern Variables (Recommended)

| Variable | Default | Description |
|----------|---------|-------------|
| `KANBAN_STORAGE_BACKEND` | `sqlite` | Storage type: `json` or `sqlite` |
| `KANBAN_DATA_DIR` | `data` | Base directory for data files |

### Legacy Variables (Deprecated)

The following variables are deprecated but still work. They will show deprecation warnings.

| Variable | Behavior | Migration |
|----------|----------|-----------|
| `KANBAN_DATABASE_URL` | Used as full SQLAlchemy URL | See [migration guide](#migrating-from-kanban_database_url) |
| `KANBAN_SQLITE_FILE` | Used as SQLite file path | See [migration guide](#migrating-from-kanban_sqlite_file) |

## Examples

### Default Configuration

```bash
# Uses SQLite at data/kanban.db
python -m src.kanban.main
```

### JSON Storage

```bash
KANBAN_STORAGE_BACKEND=json python -m src.kanban.main
```

### Custom Data Directory

```bash
# Custom data directory for both JSON and SQLite
KANBAN_DATA_DIR=/var/kanban python -m src.kanban.main
# Uses: /var/kanban/kanban.json (json) or /var/kanban/kanban.db (sqlite)
```

### Separate Data and Database Paths

If you need different paths for data files and the database:

```bash
# Use custom database URL (shows deprecation warning)
KANBAN_DATABASE_URL=postgresql://user:pass@localhost/kanban python -m src.kanban.main
```

## Migration Guide

### Migrating from `KANBAN_SQLITE_FILE`

**Before:**
```bash
export KANBAN_SQLITE_FILE=/var/lib/custom.db
```

**After:**
```bash
# If using default directory structure
export KANBAN_DATA_DIR=/var/lib

# Or set custom database URL (still works but shows warning)
export KANBAN_DATABASE_URL=sqlite:////var/lib/custom.db
```

### Migrating from `KANBAN_DATABASE_URL`

**Before:**
```bash
export KANBAN_DATABASE_URL=postgresql://user:pass@localhost/kanban
```

**After:**
```bash
# Still works but shows deprecation warning
# Consider if PostgreSQL is needed for your use case
# For simple deployments, SQLite is recommended
```

### Configuration Precedence

When multiple variables are set, the following precedence applies:

1. `KANBAN_DATABASE_URL` (legacy, deprecated)
2. `KANBAN_SQLITE_FILE` (legacy, deprecated)
3. `KANBAN_DATA_DIR` + `KANBAN_STORAGE_BACKEND` (modern)

## Programmatic Access

The configuration can be accessed programmatically:

```python
from src.kanban.config import get_storage_config

config = get_storage_config()
print(f"Backend: {config.backend}")
print(f"Data directory: {config.data_dir}")
print(f"JSON file: {config.json_file}")
print(f"SQLite URL: {config.sqlite_url}")
```

## Deprecation Warnings

When using legacy environment variables, you will see deprecation warnings:

```
DeprecationWarning: Environment variable 'KANBAN_DATABASE_URL' is deprecated. 
Use 'KANBAN_DATA_DIR' and 'KANBAN_STORAGE_BACKEND' instead. 
See docs/config.md for migration guide.
```

To capture these warnings in logs:

```python
import warnings
warnings.filterwarnings("default", category=DeprecationWarning)
```