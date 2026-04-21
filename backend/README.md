# Kanban Board Backend

Minimalistic Kanban Board API built with FastAPI.

## Project Structure

```
backend/
├── data/
│   └── kanban.json          # Sample data
├── src/kanban/
│   ├── __init__.py          # Package init
│   ├── config.py          # Env var config (KANBAN_DATA_DIR)
│   ├── models.py         # Domain models (Board, Column, Task, KanbanData)
│   ├── storage.py       # StorageInterface + JsonStorage
│   ├── frontend.py     # FrontendInterface + AngularMock
│   ├── service.py    # Validation + cascade logic
│   └── main.py      # FastAPI routes
├── tests/
│   └── test_storage.py  # Unit tests
└── pyproject.toml    # Project config
```

## Setup

1. Install dependencies:
```bash
cd backend
pip install -e ".[dev]"
```

2. Run server:
```bash
uvicorn src.kanban.main:app --reload
```

3. Run tests:
```bash
pytest
```

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| GET | /api/boards | List all boards |
| GET | /api/boards/{id} | Get board by ID |
| POST | /api/boards | Create board |
| PUT | /api/boards/{id} | Update board |
| DELETE | /api/boards/{id} | Delete board |
| GET | /api/boards/{id}/columns | Get columns by board |
| POST | /api/columns | Create column |
| PUT | /api/columns/{id} | Update column |
| DELETE | /api/columns/{id} | Delete column |
| GET | /api/columns/{id}/tasks | Get tasks by column |
| GET | /api/tasks/{id} | Get task by ID |
| POST | /api/tasks | Create task |
| PUT | /api/tasks/{id} | Update task |
| DELETE | /api/tasks/{id} | Delete task |
| GET | /api/accounts | List all accounts |
| GET | /api/accounts/{id} | Get account by ID |

## Configuration

| Environment Variable | Description | Default |
|------------------|------------|---------|
| KANBAN_DATA_DIR | Data directory path | data |

## Features

- REST API with JSON
- Strategy pattern for storage (interchangeable)
- Mock frontend for testing
- Foreign key validation
- Cascade delete (board → columns → tasks)
- Auto-cleanup of invalid references
- RFC 7807 error format
- No authentication (development)

## Testing

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).