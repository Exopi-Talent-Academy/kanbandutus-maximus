# Software Design Document

## 1. System Overview

### 1.1 Architecture

```
┌─────────────┐     HTTP      ┌──────────────┐     Storage      ┌────────────┐
│   Angular  │ ───────────► │  FastAPI     │ ◄───────────► │  JSON    │
│   Frontend  │ ◄────────── │  Backend     │                │  File    │
│  (Port 4200)│   JSON      │  (Port 8000) │                └──────────┘
└─────────────┘               └──────────────┘                └──────────┘
                                          │                 
                                          │                 
                                          ▼                 
                                  ┌──────────────┐
                                  │  SQLite    │
                                  │  (default) │
                                  └──────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version |
|-------|-----------|--------|
| Frontend Framework | Angular | 19 |
| Backend Framework | FastAPI | >=0.109.0 |
| ORM | SQLAlchemy | >=2.0 |
| Database | SQLite (default) | - |
| Server | Uvicorn | >=0.27.0 |
| Validation | Pydantic | >=2.5.0 |
| Testing | pytest | >=8.0.0 |

### 1.3 Configuration

The system supports configurable storage backends and database connections.

**Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `KANBAN_STORAGE_BACKEND` | `sqlite` | Storage type: `json` or `sqlite` |
| `KANBAN_DATABASE_URL` | `sqlite:///data/kanban.db` | Database connection string |
| `KANBAN_DATA_DIR` | `data` | Data directory |
| `KANBAN_SQLITE_FILE` | `data/kanban.db` | SQLite file path |
| `KANBAN_CORS_ORIGINS` | - | Comma-separated CORS origins |

---

## 2. API Specification

### 2.1 Base Configuration

- **Base URL:** `http://localhost:8000`
- **API Prefix:** `/api`
- **Content-Type:** `application/json`
- **Documentation:** `http://localhost:8000/docs` (Swagger UI)

### 2.2 Endpoints

#### Boards

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/boards` | Active | List all boards |
| GET | `/api/boards/{board_id}` | Active | Get board by ID |

#### Columns

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| POST | `/api/columns` | Active | Create new column |
| PUT | `/api/columns/{column_id}` | Active | Update column |
| DELETE | `/api/columns/{column_id}` | Active | Delete column |

#### Tasks

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/columns/{column_id}/tasks` | Active | Get tasks for column |
| POST | `/api/tasks` | Active | Create new task |
| PUT | `/api/tasks/{task_id}` | Active | Update task |
| DELETE | `/api/tasks/{task_id}` | Active | Delete task |

#### Accounts

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/accounts` | Active | List all accounts |
| GET | `/api/accounts/{account_id}` | Active | Get account by ID |

### 2.3 Request/Response Schemas

#### TaskCreate
```json
{
  "title": "string",
  "description": "string",
  "column_id": 1,
  "position": 0
}
```

#### TaskUpdate
```json
{
  "title": "string",
  "description": "string",
  "column_id": 1,
  "position": 0
}
```

#### ColumnCreate
```json
{
  "name": "string",
  "position": 0,
  "board_id": 1
}
```

#### BoardResponse
```json
{
  "id": 1,
  "name": "My Board",
  "columns": [
    {
      "id": 1,
      "name": "To Do",
      "position": 0,
      "board_id": 1,
      "tasks": [
        {
          "id": 1,
          "title": "Task 1",
          "description": "Description",
          "assignee": "",
          "column_id": 1,
          "position": 0
        }
      ]
    }
  ]
}
```

### 2.4 Error Handling

All error responses follow RFC 7807 format:
```json
{
  "type": "https://api.example.com/errors/{error-type}",
  "title": "Human-readable error title",
  "status": 404,
  "detail": "Detailed error message"
}
```

### 2.5 CORS Configuration

Cross-Origin Resource Sharing is enabled. Default origins:
- `http://localhost:4200` (Angular dev server)
- `http://localhost:3000` (React/Vue dev server)

Configure via `KANBAN_CORS_ORIGINS` environment variable.

---

## 3. Data Models

### 3.1 Domain Models

```python
@dataclass
class Board:
    id: int
    name: str
    columns: list[Column]

@dataclass
class Column:
    id: int
    name: str
    position: int
    board_id: int
    tasks: list[Task]

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
```

### 3.2 ORM Models (SQLAlchemy)

```python
class BoardORM(Base):
    __tablename__ = "board"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    columns: Mapped[list[ColumnORM]] = relationship(cascade="all, delete-orphan")

class ColumnORM(Base):
    __tablename__ = "columns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    board_id: Mapped[int] = mapped_column(ForeignKey("board.id", ondelete="CASCADE"))
    tasks: Mapped[list[TaskORM]] = relationship(cascade="all, delete-orphan")

class TaskORM(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), default="")
    assignee: Mapped[str] = mapped_column(String(50), default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    column_id: Mapped[int] = mapped_column(ForeignKey("columns.id", ondelete="CASCADE"))

class AccountORM(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
```

### 3.3 Entity Relationships

```
Board (1) ──────< Column (N)
     │                  │
     │                  │
     └──────────────────┤
                        │
Column (1) ──────< Task (N)
```

### 3.4 Cascade Rules

- Deleting a **Board** deletes all its **Columns** and their **Tasks**
- Deleting a **Column** deletes all its **Tasks**

---

## 4. Component Design

### 4.1 Layered Architecture

```
┌──────────────���─��────────────────────┐
│     External Clients (HTTP)          │
└─────────────────────────────────────┘
                  │
                  ▼
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
│  (Strategy Pattern)               │
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

### 4.2 Storage Strategy Pattern

The `StorageInterface` abstract class defines the contract for all storage implementations:

```python
class StorageInterface(ABC):
    @abstractmethod
    def load(self) -> KanbanData: pass

    @abstractmethod
    def save(self, data: KanbanData) -> None: pass

    @abstractmethod
    def get_board(self, board_id: int) -> Optional[Board]: pass
    # ... other CRUD methods
```

Concrete implementations:
- **JsonStorage**: JSON file-based persistence
- **SqlAlchemyStorage**: SQLAlchemy ORM with database

### 4.3 Frontend Component Hierarchy

```
App
├── NavBar
├── Header
└── Board
    └── EachColumn (for each column)
        ├── AddNewTask
        └── EachRow (for each task)
            └── Task
                └── TaskForm (edit mode)
```

### 4.4 Backend Directory Structure

```
backend/
├── src/kanban/
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── models.py        # Domain models
│   ├── orm_models.py  # SQLAlchemy ORM models
│   ├── db.py         # Database engine setup
│   ├── storage.py     # Storage abstraction (Strategy Pattern)
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
│   └── kanban.json  # Default JSON data (fallback)
└── pyproject.toml
```

### 4.5 Frontend Directory Structure

```
frontend/src/
├── app/
│   ├── app.config.ts
│   ├── app.routes.ts
│   ├── models/
│   │   └── types.ts     # TypeScript interfaces
│   ├── services/
│   │   └── tasks.ts     # HTTP service + state
│   ├── components/
│   │   ├── board/
│   │   ├── each-column/
│   │   ├── each-row/
│   │   ├── task/
│   │   ├── task-form/
│   │   ├── add-new-task/
│   │   ├── header/
│   │   └── nav-bar/
│   └── shared/
│       └── container/
└── styles.css
```