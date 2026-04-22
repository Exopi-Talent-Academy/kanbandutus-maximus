# Code Review - Known Issues

This document tracks known issues identified during code review of the Kanban backend implementation.

---

## All Issues (Complete List)

| Severity | Category | Issue | In-Scope | Location |
|----------|----------|------|----------|----------|
| CRITICAL | Security | Passwords stored in plain text, no hashing | NO | `models.py:35` |
| CRITICAL | Security | Accounts endpoint exposes `password_hash` to any client | NO | `main.py:204-214` |
| HIGH | Architecture | ID race condition: `max(id) + 1` pattern | NO | `storage.py:66-73`, `:568`, `:638`, `:709` |
| HIGH | Architecture | JsonStorage no file locking - data loss under concurrent access | NO | `storage.py:127-395` |
| HIGH | Tests | No validation tests (empty strings, invalid types) | YES | Test suite |
| HIGH | Tests | No tests for board mutation endpoints | YES | Test suite |
| MEDIUM | API | Board CRUD endpoints commented out - incomplete feature | NO | `main.py:93-121` |
| MEDIUM | API | No input validation for empty strings, negative positions | YES | `main.py`, `service.py` |
| MEDIUM | Architecture | SqlAlchemyStorage uses destructive "delete all + re-insert" | YES | `storage.py:500-544` |
| MEDIUM | Tests | No account mutation tests | YES | Test suite |
| LOW | API | Inconsistent DELETE response codes (task returns 200, others 204) | YES | `main.py:183` |
| LOW | API | No pagination on list endpoints | YES | `main.py:81-82`, `:204-206` |
| LOW | Data Model | Domain unlimited field length; ORM limited to 50/200 | YES | `models.py` vs `orm_models.py` |
| LOW | Data Model | Table naming inconsistent: `board` (singular) vs `columns/tasks/accounts` (plural) | YES | `orm_models.py` |

---

## Summary

| Status | Count |
|--------|-------|
| **IN-SCOPE** | 9 |
| **OUT-OF-SCOPE** | 5 |

## Issues Out of Scope

The following issues are identified but not addressed in current sprint:

| Severity | Category | Issue |
|----------|----------|------|
| CRITICAL | Security | Passwords stored in plain text, no hashing |
| CRITICAL | Security | Accounts endpoint exposes `password_hash` to any client |
| HIGH | Architecture | ID race condition: `max(id) + 1` pattern |
| HIGH | Architecture | JsonStorage no file locking - data loss under concurrent access |
| MEDIUM | API | Board CRUD endpoints commented out - incomplete feature |

## In-Scope Issues

### HIGH Priority

| # | Category | Issue | Location |
|---|----------|------|----------|
| 1 | Tests | No validation tests (empty strings, invalid types) | Test suite |
| 2 | Tests | No tests for board mutation endpoints | Test suite |

### MEDIUM Priority

| # | Category | Issue | Location |
|---|----------|------|----------|
| 3 | API | No input validation for empty strings, negative positions | `main.py`, `service.py` |
| 4 | Architecture | SqlAlchemyStorage uses destructive "delete all + re-insert" | `storage.py:500-544` |
| 5 | Tests | No account mutation tests | Test suite |

### LOW Priority

| # | Category | Issue | Location |
|---|----------|------|----------|
| 6 | API | Inconsistent DELETE response codes (task returns 200, others 204) | `main.py:183` |
| 7 | API | No pagination on list endpoints | `main.py:81-82`, `:204-206` |
| 8 | Data Model | Domain unlimited field length; ORM limited to 50/200 | `models.py` vs `orm_models.py` |
| 9 | Data Model | Table naming inconsistent: `board` (singular) vs `columns/tasks/accounts` (plural) | `orm_models.py` |

---

*Last updated: 2026-04-22*