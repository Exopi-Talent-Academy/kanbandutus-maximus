# Kanban Board Backend

Minimalistic Kanban Board API built with FastAPI.

---

## Running the Backend

1. Activate the virtual environment:
```bash
source virtual-environment-kanban/bin/activate
```

2. Run the server:
```bash
uvicorn src.kanban.main:app --reload
```

The API will be available at http://localhost:8000

---

## User Guide

### Installation

```bash
cd backend
pip install -e ".[dev]"
```

### Testing the Backend

Run all tests:
```bash
pytest
```

Run a specific layer:
```bash
pytest 00_test_storage.py    # Storage layer (innermost)
pytest 01_test_service.py # Service layer
pytest 02_test_validation.py # Validation layer
pytest 03_test_api.py    # API layer (outermost)
```

### Test Organization

Tests are organized by layer (innermost to outermost):

| File | Layer | Description |
|------|-------|-------------|
| `00_test_storage.py` | Storage | Data persistence tests |
| `01_test_service.py` | Service | Business logic tests |
| `02_test_validation.py` | Validation | Input validation tests |
| `03_test_api.py` | API | HTTP endpoint tests |

---

## Regression Testing

### What is Regression Testing?

Regression testing is a technique to verify that code changes haven't broken existing functionality. You run the same tests before and after making changes, then compare the results to ensure nothing unexpected broke.

**Why use it?**

- Ensures refactoring doesn't break existing features
- Catches bugs introduced by new changes
- Provides confidence when modifying code

### Running Regression Tests

1. Run tests and save results:
```bash
python -m pytest --tb=no tests > current_results.log
```

2. Compare against baseline:
```bash
diff current_results.log docs/baseline-test-results.log
```

### Interpreting Results

| Output | Meaning |
|--------|---------|
| **No differences** | Implementation unchanged ✅ |
| **NEW failures in diff** | Regression introduced ❌ |
| **Fewer failures** | Refactoring fixed issues |

### Known Baseline Failures (25 tests)

These tests fail consistently and are expected:

| Category | Failures | Reason |
|----------|---------|--------|
| Service layer | 16 | Returns None/False instead of raising NotFoundError |
| Validation layer | 8 | Empty strings and negative positions not rejected |
| API layer | 1 | Test data flakiness |

**A rule of thumb**: If you see failures NOT in this list, investigate them - they may indicate a regression.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/boards` | List all boards |
| GET | `/api/boards/{id}` | Get board by ID |
| GET | `/api/columns/{id}/tasks` | Get tasks by column |
| POST | `/api/columns` | Create column |
| PUT | `/api/columns/{id}` | Update column |
| DELETE | `/api/columns/{id}` | Delete column |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| GET | `/api/accounts` | List all accounts |
| GET | `/api/accounts/{id}` | Get account by ID |

**Note**: Board CRUD endpoints (POST/PUT/DELETE /api/boards) are currently commented out in the implementation.

---

## Project Structure

```
backend/
├── data/
│   └── kanban.json              # Sample data
├── src/kanban/
│   ├── __init__.py             # Package init
│   ├── cli.py                 # CLI utilities
│   ├── config.py              # Environment configuration
│   ├── db.py                 # Database setup
│   ├── main.py               # FastAPI routes
│   ├── models.py              # Domain models
│   ├── orm_models.py        # SQLAlchemy ORM models
│   ├── service.py           # Business logic
│   └── storage.py          # Storage abstraction
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── 00_test_storage.py # Storage layer tests
│   ├── 01_test_service.py # Service layer tests
│   ├── 02_test_validation.py # Validation tests
│   └── 03_test_api.py    # API layer tests
├── docs/
│   ├── baseline-test-results.log  # Regression baseline
│   ├── software-design-document.md
│   ├── code-review.md
│   └── decisions/          # Architecture decisions
├── alembic/                # Database migrations
├── pyproject.toml
└── run_backend.sh
```

---

## Configuration

| Environment Variable | Description | Default |
|------------------|-------------|---------|
| `KANBAN_DATA_DIR` | Data directory path | data |
| `KANBAN_STORAGE_BACKEND` | Storage type (json or sqlite) | sqlite |
| `KANBAN_DATABASE_URL` | Database URL | sqlite:///data/kanban.db |
| `KANBAN_CORS_ORIGINS` | CORS allowed origins | * |

---

## Features

- REST API with FastAPI
- Dual storage backends (JSON file + SQLite)
- Strategy pattern for interchangeable storage
- SQLAlchemy ORM with migrations
- Pydantic request/response validation
- RFC 7807 error format
- Cascading deletes (board → columns → tasks)
- No authentication (development mode)

---

## Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI - an interactive API explorer where you can test endpoints directly in the browser.