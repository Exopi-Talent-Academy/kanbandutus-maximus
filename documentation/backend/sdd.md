# Software Design Document - Backend

## 1. System Overview

### 1.1 Architecture

```
┌──────────────┐     HTTP     ┌──────────────┐     Storage     ┌────────────┐
│   Client    │ ─────────► │  FastAPI   │ ◄──────────► │   JSON    │
│             │  JSON      │  Backend   │              │   File    │
└──────────────┘            └──────────────┘              └──────────┘
                                                    
                                                    
                                                 ▼
                                          ┌──────────────┐
                                          │   SQLite    │
                                          │  (default) │
                                          └──────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version |
|-------|-----------|--------|
| Backend Framework | FastAPI | >=0.109.0 |
| ORM | SQLAlchemy | >=2.0 |
| Database | SQLite (default) | - |
| Server | Uvicorn | >=0.27.0 |
| Validation | Pydantic | >=2.5.0 |
| Testing | pytest | >=8.0.0 |

---

## 2. Architecture

### 2.1 Layered Architecture

```
┌─────────────────────────────────────┐
│  Layer 1: FastAPI Application       │
│  - REST endpoints                 │
│  - Pydantic validation           │
│  - RFC 7807 error handling       │
│  - CORS middleware              │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Layer 2: KanbanService           │
│  - Business logic                │
│  - Entity validation            │
│  - NotFoundError exceptions     │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Layer 3: Storage Interface       │
│  - JsonStorage               │
│  - SqlAlchemyStorage        │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Layer 4: Data Source            │
│  - JSON file                 │
│  - SQLite database           │
└─────────────────────────────────────┘
```

### 2.2 Storage Strategy Pattern

Storage supports pluggable backends via abstract interface:

- **JsonStorage**: JSON file-based persistence
- **SqlAlchemyStorage**: SQLAlchemy ORM with database

---

## 3. Component Design

### 3.1 Backend Directory Structure

```
backend/
├── src/kanban/
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── models.py        # Domain models
│   ├── orm_models.py  # SQLAlchemy ORM models
│   ├── db.py         # Database engine setup
│   ├── storage.py     # Storage abstraction
│   ├── service.py    # Business logic
│   ├── main.py      # FastAPI application
│   └── cli.py      # CLI commands
├── tests/
│   ├── conftest.py
│   ├── test_storage.py
│   ├── test_api_boards.py
│   ├── test_api_columns.py
│   ├── test_api_tasks.py
│   └── test_api_accounts.py
├── alembic/
│   └── versions/      # Database migrations
├── data/
│   └── kanban.json  # Default JSON data
└── pyproject.toml
```

### 3.2 API Configuration

- **Base URL:** `http://localhost:8000`
- **API Prefix:** `/api`
- **Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 4. Data Model

### 4.1 Domain Models

```
Board ────< Column ────< Task
```

### 4.2 Entities

| Entity | Fields |
|--------|--------|
| Board | id, name |
| Column | id, name, position, board_id |
| Task | id, title, description, column_id, position, assignee |
| Account | id, username, password_hash |

### 4.3 Cascade Rules

- Deleting a **Board** deletes all its **Columns** and their **Tasks**
- Deleting a **Column** deletes all its **Tasks**

---

## 5. Configuration

### 5.1 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KANBAN_STORAGE_BACKEND` | `sqlite` | Storage type: `json` or `sqlite` |
| `KANBAN_DATABASE_URL` | `sqlite:///data/kanban.db` | Database connection string |
| `KANBAN_DATA_DIR` | `data` | Data directory |
| `KANBAN_SQLITE_FILE` | `data/kanban.db` | SQLite file path |
| `KANBAN_CORS_ORIGINS` | - | Comma-separated CORS origins |

---

## 6. Deployment

Run via:
```bash
uvicorn src.kanban.main:app --reload
```

Or via provided shell script.