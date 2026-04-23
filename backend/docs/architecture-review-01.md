# Architecture Review - Kanban Backend

**Date**: 2026-04-23
**Scope**: `src/kanban/` (application code only)
**Review Type**: Fresh independent assessment

---

## Executive Summary

This architecture review provides an independent assessment of the Kanban backend codebase, comparing it against established best practices for Python REST APIs. The review identifies significant architectural concerns across security, data layer design, API maturity, and code organization.

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Count | 2 | 4 | 8 | 6 |

---

## Phase 1: Architectural Pattern Analysis

### 1.1 Layered Architecture Assessment

**Finding**: The codebase implements a three-layer architecture (FastAPI → KanbanService → Storage), but the middle layer adds minimal value.

| Layer | Implementation | Value Assessment |
|-------|--------------|----------------|
| API Layer | main.py (214 lines) | Good - handles HTTP, validation, errors |
| Service Layer | service.py (128 lines) | **Poor** - thin pass-through with null checks |
| Storage Layer | storage.py (771 lines) | Good - dual implementations |

**Issue #1 - Thin Service Layer** (MEDIUM)
- **Location**: `service.py`
- **Problem**: `KanbanService` methods are 1:1 wrappers around storage with null checks only
- **Impact**: Extra indirection provides no business logic; violates Single Responsibility Principle
- **Example**: `get_board()` at line 18-22 simply calls `storage.get_board()` and checks if None

```python
# service.py:18-22 - Typical service method
def get_board(self, board_id: int) -> Board:
    board = self.storage.get_board(board_id)
    if not board:
        raise NotFoundError("Board", board_id)
    return board
```

**Recommendation**: Either remove the service layer and call storage directly, or add real business logic (validation rules, business invariants).

---

### 1.2 Abstraction Over-Engineering

**Issue #2 - Excessive Interface** (MEDIUM)
- **Location**: `storage.py:15-74`
- **Problem**: `StorageInterface` declares 18 abstract methods, forcing both implementations to duplicate identical signatures
- **Impact**: Adding a new entity requires editing 3 files (Interface, JsonStorage, SqlAlchemyStorage)

**Recommendation**: Consider a more generic repository pattern or entity-specific interfaces.

---

### 1.3 Domain/DTO Coupling

**Issue #3 - Domain Model Leakage** (MEDIUM)
- **Location**: Domain models in `models.py` directly used in API responses
- **Problem**: `Board`, `Column`, `Task` dataclasses serve as both domain entities and API response DTOs
- **Impact**: Changing domain model breaks API contract; tight coupling

**Recommendation**: Introduce separate response DTOs using Pydantic models for API boundaries.

---

## Phase 2: Security Review

### 2.1 Authentication & Authorization

**Issue #4 - No Authentication** (CRITICAL)
- **Location**: `docs/decisions/009_no-authentication_accepted.md`
- **Finding**: System has no authentication or authorization
- **Impact**: Any client can access all data without credentials
- **Severity**: CRITICAL (architectural decision, but significant risk)

**Note**: This is an intentional architectural decision per ADR 009. The review flags it for awareness.

---

### 2.2 Password Storage

**Issue #5 - Password Hashing Absent** (CRITICAL)
- **Location**: `models.py:35`, `orm_models.py:54`
- **Problem**: Account passwords stored in plaintext in `password_hash` field
- **Code**:
```python
# models.py:31-35 - Account with plain text "hash"
@dataclass
class Account:
    id: int
    username: str
    password_hash: str  # Stores plaintext, not hash
```
- **Impact**: Security vulnerability if accounts table is exposed

---

### 2.3 Data Exposure

**Issue #6 - Password Field Exposed** (HIGH)
- **Location**: `main.py:204-206`, API responses
- **Problem**: `password_hash` field included in all account responses
- **API Response**:
```json
{
  "id": 1,
  "username": "admin",
  "password_hash": "secret123"
}
```
- **Impact**: Any API client can read all stored passwords

---

### 2.4 Input Validation

**Issue #7 - No Input Validation** (MEDIUM)
- **Location**: `main.py`, `service.py`
- **Problem**: No validation for:
  - Empty strings in required fields (name, title)
  - Negative positions
  - Invalid entity IDs passed as foreign keys
- **Example**: `TaskCreate` at line 52-56 accepts any string without length limits

**Recommendation**: Add Pydantic validators with constraints (min_length, max_length, gt for positions).

---

## Phase 3: Data Layer & Persistence

### 3.1 ID Generation Race Conditions

**Issue #8 - Race Condition in ID Generation** (HIGH)
- **Location**: `storage.py:568`, `:638`, `:709`
- **Problem**: Uses `max(id) + 1` pattern without locking
- **Code**:
```python
# storage.py:568-569 - SqlAlchemyStorage
max_id = session.scalar(select(BoardORM.id).order_by(BoardORM.id.desc()).limit(1)) or 0
board = BoardORM(id=max_id + 1, name=name)
```
- **Impact**: Concurrent requests can generate duplicate IDs
- **Severity**: HIGH for production multi-instance deployments

**Recommendation**: Use database auto-increment (SERIAL/IDENTITY) or distributed ID generation (Snowflake).

---

### 3.2 JsonStorage Concurrent Access

**Issue #9 - No File Locking** (HIGH)
- **Location**: `storage.py:140-142`
- **Problem**: JsonStorage has no file locking for concurrent access
- **Code**:
```python
# storage.py:140-142 - No locking
def _write_file(self, data: dict) -> None:
    with open(self.data_file, "w") as f:
        json.dump(data, f, indent=2)
```
- **Impact**: Data loss/corruption under concurrent writes
- **Use Case**: Only safe for single-instance development

---

### 3.3 Destructive Save Pattern

**Issue #10 - Destructive Re-Insert Pattern** (MEDIUM)
- **Location**: `storage.py:500-544`
- **Problem**: `SqlAlchemyStorage.save()` deletes ALL records then re-inserts
- **Code**:
```python
# storage.py:503-508 - Destructive save
with session.begin():
    session.execute(delete(AccountORM))
    session.execute(delete(TaskORM))
    session.execute(delete(ColumnORM))
    session.execute(delete(BoardORM))
    session.add_all([...])  # Re-inserts everything
```
- **Impact**: Loss of database-specific features (auto-timestamps, triggers), inefficient
- **Recommendation**: Use standard CRUD operations or upsert patterns

---

### 3.4 Schema Inconsistencies

**Issue #11 - Field Length Mismatch** (LOW)
- **Location**: `models.py` vs `orm_models.py`
- **Problem**: Domain models have no limits; ORM has constraints
  - `Board.name`: No limit (domain) vs String(50) (ORM)
  - `Task.title`: No limit (domain) vs String(50) (ORM)
  - `Task.description`: No limit (domain) vs String(200) (ORM)

---

## Phase 4: API Design Maturity

### 4.1 Inconsistent Response Codes

**Issue #12 - DELETE Response Code Inconsistency** (LOW)
- **Location**: `main.py:183` vs `:146`
- **Finding**: 
  - `delete_task()` returns 200 (`@app.delete("/api/tasks/{task_id}", status_code=200)`)
  - `delete_column()` returns default 204
  - `delete_board()` would return default 204
- **Impact**: Client must handle different success codes

---

### 4.2 Missing Feature - Pagination

**Issue #13 - No Pagination** (LOW)
- **Location**: `main.py:81-82`, `:204-206`
- **Problem**: List endpoints (`/api/boards`, `/api/accounts`) return all records
- **Impact**: Performance degradation with large datasets

---

### 4.3 Board CRUD Incomplete

**Issue #14 - Board Endpoints Commented Out** (LOW)
- **Location**: `main.py:93-121`
- **Finding**: Board create/update/delete endpoints commented out
- **Impact**: Users cannot modify boards via API

---

## Phase 5: Code Quality

### 5.1 Import Inside Function

**Issue #15 - Import Inside Handler** (LOW)
- **Location**: `main.py:68`
- **Problem**: `JSONResponse` imported inside exception handler
- **Code**:
```python
# main.py:66-68 - Import inside function
@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc: NotFoundError):
    from fastapi.responses import JSONResponse  # Should be at top
```

---

### 5.2 Missing Return Type Hints

**Issue #16 - Missing Return Types** (LOW)
- **Finding**: Many functions lack return type annotations
- **Examples**: `get_boards()`, `create_column()`, all service methods

---

## Phase 6: Best Practice Comparison

### Python/Language Standards

| Practice | Standard | Status | Issue |
|----------|----------|--------|-------|
| Type hints | PEP 484 | Partial | Missing on ~15 functions |
| Docstrings | PEP 257 | Missing | No docstrings on public APIs |
| Optional use | Modern | Inconsistent | Some use `Optional[X]`, some `X \| None` |

### FastAPI Best Practices

| Practice | Standard | Status | Issue |
|----------|----------|--------|-------|
| Exception handling | RFC 7807 | Implemented | Good |
| Pydantic validation | v2.x | Partial | No validators defined |
| dependency Injection | DI container | Not used | Direct instantiation in main.py |

### SQLAlchemy 2.0 Patterns

| Practice | Standard | Status | Issue |
|----------|----------|--------|-------|
| ORM models | Declarative | Good | Modern style |
| Relationships | selectinload | Good | Used |
| Transactions | Explicit begin() | Partial | Mixed patterns |

---

## Issues Summary

### Critical (2)

| # | Category | Issue | Location |
|---|----------|-------|----------|
| 1 | Security | No authentication (intentional decision) | ADR 009, main.py |
| 2 | Security | Passwords stored in plaintext | models.py:35, orm_models.py:54 |

### High (4)

| # | Category | Issue | Location |
|---|----------|-------|----------|
| 3 | Security | password_hash exposed in API responses | main.py:204-206 |
| 4 | Data | ID generation race condition (max+1) | storage.py:568, 638, 709 |
| 5 | Data | JsonStorage no file locking | storage.py:140-142 |
| 6 | Architecture | Thin service layer (pass-through) | service.py |

### Medium (8)

| # | Category | Issue | Location |
|---|----------|-------|----------|
| 7 | Architecture | Excessive StorageInterface (18 methods) | storage.py:15-74 |
| 8 | Architecture | Domain model leakage to API | models.py |
| 9 | API | No input validation | main.py Pydantic models |
| 10 | Data | Destructive save pattern | storage.py:500-544 |
| 11 | Code Quality | Import inside function | main.py:68 |
| 12 | API | Board CRUD endpoints commented out | main.py:93-121 |
| 13 | Architecture | Multiple config paths for storage | config.py |
| 14 | Testing | No validation tests | test suite |

### Low (6)

| # | Category | Issue | Location |
|---|----------|-------|----------|
| 15 | API | DELETE returns 200 vs 204 | main.py:183 |
| 16 | API | No pagination | main.py |
| 17 | Data | Field length mismatch (domain vs ORM) | models.py vs orm_models.py |
| 18 | Code Quality | Missing return type hints | main.py, service.py |
| 19 | Code Quality | Missing docstrings | main.py functions |
| 20 | Data | Table naming inconsistent | orm_models.py:8 ("board" vs "columns/tasks/accounts") |

---

## Recommendations Summary

### Should Fix (High Priority)

1. **Separate password handling**: Never expose `password_hash` in API responses
2. **Add input validation**: Use Pydantic validators for strings, positions
3. **Use database auto-increment**: Replace `max(id)+1` with database sequences

### Consider Fixing (Medium Priority)

4. **Add real business logic to service layer** or remove it
5. **Implement proper CRUD in SqlAlchemyStorage** instead of delete-all + re-insert
6. **Add file locking to JsonStorage** or deprecate
7. **Introduce API response DTOs** separate from domain models

### Nice to Have (Low Priority)

8. **Add pagination** to list endpoints
9. **Standardize DELETE response codes** to 204
10. **Add return type hints and docstrings**

---

## References

- Architecture Decision Records: `docs/decisions/`
- Software Design Document: `docs/software-design-document.md`
- Prior Code Review: `docs/code-review.md`
- Code Quality Review: `docs/code-quality-review.md`

---

*Generated: 2026-04-23*