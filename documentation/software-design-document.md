# Software Design Document

## 1. System Overview

### 1.1 Purpose
This document describes the architecture and design of the Kanban Board API backend, a REST API service for managing Kanban boards with boards, columns, and tasks.

### 1.2 Scope
- REST API endpoints for CRUD operations on boards, columns, and tasks
- JSON file-based persistence
- Integration with Angular frontend via HTTP

### 1.3 System Context
```
┌─────────────┐     HTTP      ┌──────────────┐     HTTP     ┌────────────┐
│   Angular   │ ────────────► │  FastAPI     │ ───────────► │   JSON     │
│   Frontend  │ ◄──────────── │  Backend     │              │   File     │
│  (Port 4200)│    JSON       │  (Port 8000) │              │  Storage   │
└─────────────┘               └──────────────┘              └────────────┘
```

---

## 2. Architectural Style

### 2.1 Pattern
Layered Architecture with Strategy Pattern for interchangeable components.

### 2.2 Layers
```
┌─────────────────────────────────────┐
│     External Clients (HTTP)        │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Layer 1: FastAPI Application       │
│  - REST endpoints                   │
│  - Pydantic validation              │
│  - RFC 7807 error handling          │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Layer 2: KanbanService             │
│  - Business logic                   │
│  - Entity validation                 │
│  - NotFoundError exceptions         │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Layer 3: Storage                    │
│  - StorageInterface (abstract)      │
│  - JsonStorage (concrete)           │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Data: JSON file                    │
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

**Key Classes/Functions:**
- `app`: FastAPI application instance
- `BoardCreate`, `BoardUpdate`: Pydantic models for board operations
- `ColumnCreate`, `ColumnUpdate`: Pydantic models for column operations
- `TaskCreate`, `TaskUpdate`: Pydantic models for task operations
- `not_found_handler`: Global exception handler for NotFoundError

**Public API:**
- GET `/api/boards`
- GET `/api/boards/{board_id}`
- POST `/api/tasks`
- PUT `/api/tasks/{task_id}`

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
- `get_board(board_id)`, `get_all_boards()`
- `create_board(name)`, `update_board(board_id, name)`, `delete_board(board_id)`
- `get_column(column_id)`, `get_columns_by_board(board_id)`
- `create_column(name, position, board_id)`, `update_column(column_id, name, position)`, `delete_column(column_id)`
- `get_task(task_id)`, `get_tasks_by_column(column_id)`
- `create_task(title, description, column_id, position)`, `update_task(...)`, `delete_task(task_id)`

### 3.3 Storage Layer

**Module:** `storage.py`

**Responsibilities:**
- Abstract data persistence interface
- JSON file read/write operations
- Entity CRUD operations

**Key Classes:**
- `StorageInterface`: Abstract base class (Strategy Pattern)
- `JsonStorage`: Concrete JSON file implementation

**Design Pattern:**
Strategy Pattern allowing interchangeable storage backends (future: SQLiteStorage, PostgreStorage).

### 3.4 Data Models

**Module:** `models.py`

**Responsibilities:**
- Define domain entity dataclasses
- Provide helper methods for entity lookups

**Key Classes:**
```python
@dataclass
class Board:
    id: int
    name: str
    columns: list[int]  # List of column IDs

@dataclass
class Column:
    id: int
    name: str
    position: int
    board_id: int

@dataclass
class Task:
    id: int
    title: str
    column_id: int
    description: str = ""
    position: int = 0

@dataclass
class KanbanData:
    boards: list[Board]
    columns: list[Column]
    tasks: list[Task]
```

### 3.5 Configuration Module

**Module:** `config.py`

**Responsibilities:**
- Environment-based configuration
- Data directory and file path resolution

**Environment Variables:**
- `KANBAN_DATA_DIR`: Directory containing `kanban.json` (default: `data`)

### 3.6 Frontend Interface

**Module:** `frontend.py`

**Responsibilities:**
- Abstract frontend integration
- Mock implementation for testing

**Key Classes:**
- `FrontendInterface`: Abstract base class
- `AngularMock`: Mock implementation storing predefined responses

---

## 4. Data Flow

### 4.1 Read Request Flow
```
Client → GET /api/boards/1
      → main.py:get_board()
      → service.get_board(1)
      → storage.get_board(1)
      → load() from JSON
      → return Board
      → JSON response to client
```

### 4.2 Write Request Flow
```
Client → POST /api/tasks {title, column_id, ...}
      → main.py:create_task(TaskCreate)
      → service.create_task(...)
      → storage.create_task(...)
      → load() → modify → save() to JSON
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
```

### 5.2 Cascade Rules
- Deleting a **Board** deletes all its **Columns** and their **Tasks**
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
| Framework | FastAPI | >=0.109.0 |
| Server | Uvicorn | >=0.27.0 |
| Validation | Pydantic | >=2.5.0 |
| Testing | pytest | >=8.0.0 |
| HTTP Client | httpx | >=0.26.0 |

---

## 8. Directory Structure

```
backend/
├── data/
│   └── kanban.json           # JSON data store
├── docs/
│   └── ADR.md               # Architecture Decision Records
├── src/
│   └── kanban/
│       ├── __init__.py
│       ├── config.py         # Configuration
│       ├── models.py         # Domain models
│       ├── storage.py        # Storage abstraction
│       ├── frontend.py       # Frontend abstraction
│       ├── service.py        # Business logic
│       └── main.py           # FastAPI app
├── tests/
│   ├── conftest.py
│   ├── test_storage.py
│   ├── test_api_boards.py
│   └── test_api_tasks.py
├── pyproject.toml
└── run_backend.sh
```
