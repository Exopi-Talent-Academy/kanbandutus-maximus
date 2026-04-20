# MVP Kanban Board Design Document

## Intentions & Goals

| Goal | Description |
|------|-------------|
| Build a minimalistic kanban board | Web-based task management with boards, columns, and tasks |
| Frontend in Angular | SPA using Angular framework |
| Backend in Python | REST API server using FastAPI |
| Flexible architecture | Strategy pattern for interchangeable storage/frontend |
| Testable | Mock frontend for backend testing without real Angular |

## Architecture

```
+-------------------------------------------------------------+
|                    Full Application                          |
+----------------------------+--------------------------------+
|     Angular Frontend         |      Python Backend (FastAPI)   |
|     (Port 4200)              |      (Port 8000)              |
+----------------------------+--------------------------------+
|  HttpClient                |  HTTP Routes -> Service        |
|  Components               |       v                      |
|  Services                 |  Storage (Strategy Pattern)  |
|  Interceptors              |       v                      |
|                          |  JsonStorage (data/kanban.json)|
+----------------------------+--------------------------------+
```

## Strategy Pattern

| Interface | Purpose | Implementations |
|-----------|---------|---------------|
| StorageInterface | Database abstraction | JsonStorage, SQLiteStorage, PostgreStorage (future) |
| FrontendInterface | Frontend simulation | AngularMock (testing), AngularReal (production) |

## Key Design Decisions

| Decision | Choice |
|----------|--------|
| Protocol | REST API with JSON (RFC 7807 errors) |
| Backend | FastAPI |
| Storage | JSON file (data/kanban.json) |
| ORM | None (direct JSON) |
| Auth | Skipped (development/testing) |
| IDs | Auto-integer |
| Data dir | Configurable via KANBAN_DATA_DIR env |
| Error on missing file | Fail with error |

## Service Layer Validation

| Check | Behavior |
|-------|----------|
| Create task | column_id must exist |
| Create column | board_id must exist |
| Update task | target column_id must exist |
| Delete column | Cascade delete tasks in column |
| Delete board | Delete columns + tasks |
| Auto-cleanup | Remove invalid references |

## File Structure

```
backend/
+-- data/
|   +-- kanban.json
+-- src/
|   +-- kanban/
|       +-- __init__.py
|       +-- config.py
|       +-- models.py
|       +-- storage.py
|       +-- frontend.py
|       +-- service.py
|       +-- main.py
+-- tests/
|   +-- test_storage.py
+-- pyproject.toml
```

## Sample Data

```json
{
  "boards": [{"id": 1, "name": "My Board", "columns": [1, 2, 3]}],
  "columns": [
    {"id": 1, "name": "To Do", "position": 0},
    {"id": 2, "name": "In Progress", "position": 1},
    {"id": 3, "name": "Done", "position": 2}
  ],
  "tasks": [
    {"id": 1, "title": "Welcome Task", "description": "Drag me to move", "column_id": 1, "position": 0}
  ]
}
```