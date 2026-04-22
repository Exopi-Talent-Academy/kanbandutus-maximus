# Technical Specification

## 1. Introduction

### 1.1 Overview
This document specifies the technical implementation details of the Kanban Board API backend.

### 1.2 Objectives
- Provide REST API for Kanban board operations
- Support boards, columns, and tasks
- Enable Angular frontend integration
- Ensure testability with mock components

---

## 2. API Specification

### 2.1 Base Configuration
- **Base URL:** `http://localhost:8000`
- **API Prefix:** `/api`
- **Content-Type:** `application/json`
- **Documentation:** `http://localhost:8000/docs` (Swagger UI)

### 2.2 Endpoints

#### 2.2.1 Boards

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/boards` | Active | List all boards |
| GET | `/api/boards/{board_id}` | Active | Get board by ID |
| POST | `/api/boards` | Inactive | Create new board |
| PUT | `/api/boards/{board_id}` | Inactive | Update board |
| DELETE | `/api/boards/{board_id}` | Inactive | Delete board |

#### 2.2.2 Columns

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/boards/{board_id}/columns` | Inactive | Get columns for board |
| POST | `/api/columns` | Inactive | Create new column |
| PUT | `/api/columns/{column_id}` | Inactive | Update column |
| DELETE | `/api/columns/{column_id}` | Inactive | Delete column |

#### 2.2.3 Tasks

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/columns/{column_id}/tasks` | Inactive | Get tasks for column |
| GET | `/api/tasks/{task_id}` | Inactive | Get task by ID |
| POST | `/api/tasks` | Active | Create new task |
| PUT | `/api/tasks/{task_id}` | Active | Update task |
| DELETE | `/api/tasks/{task_id}` | Inactive | Delete task |

### 2.3 Request/Response Models

#### 2.3.1 BoardCreate
```json
{
  "name": "string"
}
```

#### 2.3.2 BoardUpdate
```json
{
  "name": "string"
}
```

#### 2.3.3 ColumnCreate
```json
{
  "name": "string",
  "position": 0,
  "board_id": 1
}
```

#### 2.3.4 ColumnUpdate
```json
{
  "name": "string",
  "position": 0
}
```

#### 2.3.5 TaskCreate
```json
{
  "title": "string",
  "description": "string",
  "column_id": 1,
  "position": 0
}
```

#### 2.3.6 TaskUpdate
```json
{
  "title": "string",
  "description": "string",
  "column_id": 1,
  "position": 0
}
```

#### 2.3.7 Board Response
```json
{
  "id": 1,
  "name": "My Board",
  "columns": [1, 2, 3]
}
```

#### 2.3.8 Column Response
```json
{
  "id": 1,
  "name": "To Do",
  "position": 0,
  "board_id": 1
}
```

#### 2.3.9 Task Response
```json
{
  "id": 1,
  "title": "Task Title",
  "description": "Task description",
  "column_id": 1,
  "position": 0
}
```

### 2.4 Error Responses

#### 2.4.1 Not Found Error (RFC 7807)
```json
{
  "type": "https://api.example.com/errors/board-not-found",
  "title": "Board Not Found",
  "status": 404,
  "detail": "Board with id=999 not found"
}
```

---

## 3. Data Models

### 3.1 Data Schema

#### 3.1.1 Board
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | integer | Required, Unique | Auto-generated |
| name | string | Required | Board name |
| columns | array[integer] | Optional | List of column IDs |

#### 3.1.2 Column
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | integer | Required, Unique | Auto-generated |
| name | string | Required | Column name |
| position | integer | Required | Order within board |
| board_id | integer | Required | Parent board ID |

#### 3.1.3 Task
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | integer | Required, Unique | Auto-generated |
| title | string | Required | Task title |
| description | string | Optional | Task details |
| column_id | integer | Required | Parent column ID |
| position | integer | Optional, default=0 | Order within column |

### 3.2 JSON File Format
```json
{
  "boards": [
    {"id": 1, "name": "My Board", "columns": [1, 2, 3]}
  ],
  "columns": [
    {"id": 1, "name": "To Do", "position": 0, "board_id": 1},
    {"id": 2, "name": "In Progress", "position": 1, "board_id": 1},
    {"id": 3, "name": "Done", "position": 2, "board_id": 1}
  ],
  "tasks": [
    {"id": 1, "title": "Welcome Task", "description": "Drag me to move", "column_id": 1, "position": 0}
  ]
}
```

---

## 4. Business Rules

### 4.1 Validation Rules

| Operation | Rule |
|-----------|------|
| Create Task | `column_id` must reference existing column |
| Update Task | `column_id` must reference existing column |
| Create Column | `board_id` must reference existing board |
| Delete Board | Cascade delete all columns and tasks |
| Delete Column | Cascade delete all tasks, cleanup board references |

### 4.2 ID Generation
- IDs are auto-incrementing integers
- Maximum existing ID + 1 for new entities
- Default starting ID is 1

---

## 5. Configuration

### 5.1 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KANBAN_DATA_DIR` | `data` | Directory containing kanban.json |

### 5.2 Startup Behavior
- Application fails with `FileNotFoundError` if data file is missing
- No default data is created automatically

---

## 6. Testing Specification

### 6.1 Test Framework
- **Framework:** pytest
- **HTTP Client:** httpx with FastAPI TestClient

### 6.2 Test Files
- `tests/conftest.py`: Shared fixtures
- `tests/test_storage.py`: Storage layer tests
- `tests/test_api_boards.py`: Board API tests
- `tests/test_api_tasks.py`: Task API tests

### 6.3 Test Fixtures

| Fixture | Purpose |
|---------|---------|
| `temp_data_file` | Creates temporary JSON file |
| `storage` | JsonStorage with temp file |
| `client` | FastAPI TestClient with monkeypatched config |

### 6.4 Test Coverage
- Storage CRUD operations
- Foreign key validation
- Cascade delete behavior
- API endpoint responses
- HTTP error handling (404)

---

## 7. Security Considerations

### 7.1 Current State
- No authentication implemented
- No authorization checks
- No input length limits
- No rate limiting

### 7.2 Known Limitations
- File path injection possible via `KANBAN_DATA_DIR`
- No SQL injection risk (no database)
- No CORS configuration

---

## 8. Performance Characteristics

### 8.1 Storage Operations
- Every operation reads entire JSON file
- No caching or connection pooling
- File written on every create/update/delete

### 8.2 Expected Limitations
- Performance degrades with dataset size
- Concurrent writes may cause race conditions
- Not suitable for high-traffic production use

---

## 9. Dependencies

### 9.1 Production
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.109.0 | Web framework |
| uvicorn | >=0.27.0 | ASGI server |
| pydantic | >=2.5.0 | Data validation |

### 9.2 Development
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.0.0 | Testing framework |
| httpx | >=0.26.0 | HTTP client for tests |

---

## 10. Non-Functional Requirements

### 10.1 Platform
- Python >= 3.11
- Cross-platform (Linux, macOS, Windows)

### 10.2 Deployment
- Run via: `uvicorn src.kanban.main:app --reload`
- Or via: `./run_backend.sh`
