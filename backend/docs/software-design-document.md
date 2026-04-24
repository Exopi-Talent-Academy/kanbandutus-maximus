# Software Design Document

## 1. System Overview

### 1.1 Purpose
This document describes the architecture and design of the Kanban Board API backend, a REST API service for managing Kanban boards with boards, columns, tasks, and accounts.

### 1.2 Scope
- REST API endpoints for CRUD operations on boards, columns, and tasks
- Dual storage backends: JSON file and SQLite (via SQLAlchemy)
- Integration with Angular frontend via HTTP

### 1.3 System Context
```
┌─────────────┐     HTTP      ┌──────────────┐     SQL/JSON   ┌────────────┐
│   Angular   │ ────────────► │  FastAPI     │ ───────────► │  SQLite    │
│   Frontend  │ ◄──────────── │  Backend     │              │  Database  │
│  (Port 4200)│    JSON       │  (Port 8000) │              │           │
└─────────────┘               └──────────────┘              └────────────┘
```

---

## 2. Architectural Style

### 2.1 Pattern
Layered Architecture with Strategy Pattern for interchangeable storage components.

### 2.2 Layers
```
┌─────────────────────────────────────┐
│     External Clients (HTTP)            │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Layer 1: FastAPI Application       │
│  - REST endpoints                 │
│  - Pydantic validation           │
│  - RFC 7807 error handling      │
│  - CORS middleware             │
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
│  Layer 3: Storage                 │
│  - StorageInterface (abstract)  │
│  - JsonStorage (concrete)       │
│  - SqlAlchemyStorage (concrete)  │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Data: SQLite / JSON file        │
└─────────────────────────────────────┘
```

---

## 3. Component Descriptions

### 3.1 FastAPI Application Layer

**Module:** `main.py`

**Responsibilities:**
- Define REST API endpoints
- Validate request bodies with Pydantic
- Handle HTTP exceptions
- Register global exception handlers
- CORS configuration

**Key Classes/Functions:**
- `app`: FastAPI application instance
- `BoardCreate`, `BoardUpdate`: Pydantic models (defined but unused - board CRUD endpoints commented out)
- `ColumnCreate`, `ColumnUpdate`: Pydantic models for column operations
- `TaskCreate`, `TaskUpdate`: Pydantic models for task operations
- `not_found_handler`: Global exception handler for NotFoundError

**Active API Endpoints:**

| Method | Endpoint | Handler |
|--------|----------|---------|
| GET | `/api/boards` | `get_boards()` |
| GET | `/api/boards/{board_id}` | `get_board()` |
| POST | `/api/columns` | `create_column()` |
| PUT | `/api/columns/{column_id}` | `update_column()` |
| DELETE | `/api/columns/{column_id}` | `delete_column()` |
| GET | `/api/columns/{column_id}/tasks` | `get_tasks()` |
| POST | `/api/tasks` | `create_task()` |
| PUT | `/api/tasks/{task_id}` | `update_task()` |
| DELETE | `/api/tasks/{task_id}` | `delete_task()` |
| GET | `/api/accounts` | `get_accounts()` |
| GET | `/api/accounts/{account_id}` | `get_account()` |

**Commented Out Endpoints:**
- POST/PUT/DELETE `/api/boards`
- GET `/api/boards/{board_id}/columns`
- GET `/api/tasks/{task_id}`

### 3.2 Service Layer

**Module:** `service.py`

**Responsibilities:**
- Implement business logic
- Validate entity relationships (e.g., task must belong to existing column)
- Raise NotFoundError for missing entities

**Key Classes:**
- `NotFoundError`: Custom exception with entity type and ID
- `KanbanService`: Facade for all business operations

**Public Methods:**
- Board: `get_board()`, `get_all_boards()`, `create_board()`, `update_board()`, `delete_board()`
- Column: `get_column()`, `get_columns_by_board()`, `create_column()`, `update_column()`, `delete_column()`
- Task: `get_task()`, `get_tasks_by_column()`, `create_task()`, `update_task()`, `delete_task()`
- Account: `get_account()`, `get_all_accounts()`

### 3.3 Storage Layer

**Module:** `storage.py`

**Responsibilities:**
- Abstract data persistence interface
- Dual storage backend implementations
- Entity CRUD operations
- Cascade delete handling
- Position reordering

**Key Classes:**
- `StorageInterface`: Abstract base class (Strategy Pattern)
- `JsonStorage`: JSON file implementation (development)
- `SqlAlchemyStorage`: SQLite implementation (default, production)

**Configuration:**
- Storage backend selected via `KANBAN_STORAGE_BACKEND` env var (default: `sqlite`)

### 3.4 Data Models

**Module:** `models.py`

**Domain Entities:**
```python
@dataclass
class Board:
    id: int
    name: str
    columns: list[Column]  # Nested Column objects

@dataclass
class Column:
    id: int
    name: str
    position: int
    board_id: int
    tasks: list[Task]  # Nested Task objects

@dataclass
class Task:
    id: int
    title: str
    column_id: int
    description: str = ""
    assignee: str = ""
    position: int = 0

@dataclass
class Account:
    id: int
    username: str
    password_hash: str

@dataclass
class KanbanData:
    boards: list[Board]
    columns: list[Column]
    tasks: list[Task]
    accounts: list[Account]
```

**Module:** `orm_models.py`

**Database Entities (SQLAlchemy):**
- `BoardORM`: id, name → table `board`
- `ColumnORM`: id, name, position, board_id → table `columns`
- `TaskORM`: id, title, description, assignee, position, column_id → table `tasks`
- `AccountORM`: id, username, password_hash → table `accounts`

### 3.5 Database Module

**Module:** `db.py`

**Responsibilities:**
- SQLAlchemy engine configuration
- Session management
- Database initialization

### 3.6 Configuration Module

**Module:** `config.py`

**Environment Variables:**
- `KANBAN_DATA_DIR`: Directory containing data files (default: `data`)
- `KANBAN_SQLITE_FILE`: SQLite database path (default: `data/kanban.db`)
- `KANBAN_DATABASE_URL`: Database URL (default: `sqlite:///data/kanban.db`)
- `KANBAN_STORAGE_BACKEND`: Storage type `json` or `sqlite` (default: `sqlite`)
- `KANBAN_CORS_ORIGINS`: Comma-separated CORS origins

---

## 4. Data Flow

### 4.1 Read Request Flow
```
Client → GET /api/boards/1
      → main.py:get_board()
      → service.get_board(1)
      → storage.get_board(1)
      → load() from database
      → return Board
      → JSON response to client
```

### 4.2 Write Request Flow
```
Client → POST /api/tasks {title, column_id, ...}
      → main.py:create_task(TaskCreate)
      → service.create_task(...)
      → storage.create_task(...)
      → modify → save() to database
      → return Task
      → JSON response to client
```

---

## 5. Entity Relationships

### 5.1 Data Model
```
Board (1) ──────< Column (N)
    │                  │
    │                  │
    └──────────────────┤
                       │
Column (1) ──────< Task (N)

Account: Standalone entity, no relationships
```

### 5.2 Cascade Rules
- Deleting a **Board** deletes all its **Columns** and their **Tasks** (SQLAlchemy cascade)
- Deleting a **Column** deletes all its **Tasks** and removes reference from **Board**

---

## 6. Error Handling

### 6.1 Not Found Errors
All entity lookups raise `NotFoundError(entity, entity_id)` if not found.

### 6.2 Error Response Format (RFC 7807)
```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Board Not Found",
  "status": 404,
  "detail": "Board with id=999 not found"
}
```

---

## 7. Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | >=3.11 |
| Web Framework | FastAPI | >=0.109.0 |
| ASGI Server | Uvicorn | >=0.27.0 |
| ORM | SQLAlchemy | >=2.0.0 |
| Database | SQLite | - |
| Validation | Pydantic | >=2.5.0 |
| Migrations | Alembic | >=1.13.0 |
| Testing | pytest | >=8.0.0 |
| HTTP Client | httpx | >=0.26.0 |

---

## 8. Directory Structure

```
backend/
├── alembic/                     # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── data/                       # Data files
│   ├── kanban.json            # JSON data store
│   └── kanban.db              # SQLite database
├── docs/                       # Documentation
│   ├── software-design-document.md
│   ├── decisions/             # Architecture Decision Records
│   │   ├── index.md
│   │   └── 001-010_*.md
│   ├── diagrams/
│   └── archive/              # Archived documentation
├── src/kanban/                # Main application
│   ├── __init__.py
│   ├── cli.py                 # CLI utilities
│   ├── config.py             # Configuration
│   ├── db.py                 # Database setup
│   ├── main.py               # FastAPI app & routes
│   ├── models.py             # Domain models
│   ├── orm_models.py        # SQLAlchemy ORM models
│   ├── service.py            # Business logic
│   └── storage.py            # Storage abstraction
├── tests/                     # Test suite
│   ├── conftest.py
│   ├── test_api_accounts.py
│   ├── test_api_boards.py
│   ├── test_api_columns.py
│   ├── test_api_tasks.py
│   └── test_storage.py
├── alembic.ini
├── pyproject.toml
└── run_backend.sh
```

---

## 9. Known Implementation Notes

### 9.1 Active Development
- Board CRUD endpoints (POST/PUT/DELETE) are currently commented out in `main.py`
- Account mutations (create/update/delete) are not exposed via API
- Passwords are stored in plain text (no hashing implemented)

### 9.2 Storage Backend
- Default storage is `SqlAlchemyStorage` (SQLite)
- JSON storage available for development via `KANBAN_STORAGE_BACKEND=json`
- Auto-seeds from JSON file on first run with new SQLite database

### 9.3 Database
- Uses SQLite by default with automatic migration via Alembic
- Foreign key constraints enabled for cascade deletes
- Accounts table added in separate migration

### 9.4 Architecture Decision Records
- ADRs are now maintained in `docs/decisions/` directory
- Each ADR is in its own numbered file: `001_backend-development-language_accepted.md`
- Index available at `docs/decisions/index.md`

---

## 10. Tests

### 10.1 Test Files
- `tests/conftest.py`: Shared fixtures
- `tests/test_api_accounts.py`: Account endpoint tests
- `tests/test_api_boards.py`: Board endpoint tests
- `tests/test_api_columns.py`: Column endpoint tests
- `tests/test_api_tasks.py`: Task endpoint tests
- `tests/test_storage.py`: Storage layer tests

### 10.2 Test Fixtures
- `temp_data_file`: Temporary JSON file
- `json_storage`: JsonStorage instance
- `sqlalchemy_storage`: SqlAlchemyStorage instance
- `storage`: Parametrized fixture for both backends
- `client`: FastAPI TestClient