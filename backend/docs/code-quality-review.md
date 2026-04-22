# Code Quality Review

Analysis of the Kanban backend codebase using static analysis tools and manual review.

**Date**: 2026-04-22
**Scope**: `src/` directory

---

## Tools Used

| Tool | Purpose | Issues Found |
|------|---------|-------------|
| ruff | Fast linting & style | ~80 issues |
| flake8 | Style enforcement | ~35 issues |
| pylint | Deep code analysis | ~50 issues |
| mypy | Type checking | 9 errors |
| bandit | Security | 0 issues |

---

## Summary

| Category | Issues |
|----------|--------|
| Critical | 0 |
| High | 2 (unused imports, line too long) |
| Medium | ~100 |
| Low/Style | ~150 |

---

## 1. Ruff Findings

### Fixable Issues (* = auto-fixable)

| File | Issue | Fixable |
|------|-------|--------|
| service.py:1 | F401: Unused import `Optional` | * |
| config.py:50 | W292: No newline at end of file | * |
| main.py:1 | I001: Import block unsorted | * |
| main.py:74 | COM812: Trailing comma missing | * |
| main.py:76-77 | W293: Blank line with whitespace | * |
| models.py:44,50,56 | UP045: Use `X \| None` instead of `Optional` | * |

### Docstring Issues (D1xx)

| File | Count | Issue |
|------|-------|-------|
| main.py | 15 | Missing docstrings in functions |
| models.py | 5 | Missing docstrings in classes |
| orm_models.py | 4 | Missing docstrings in classes |
| service.py | 16+ | Missing docstrings in methods |
| cli.py | 3 | Missing docstrings in functions |
| db.py | 3 | Missing docstrings in functions |

### Style Issues

| File | Count | Issue |
|------|-------|-------|
| main.py | ~15 | W291: Trailing whitespace |
| main.py | 3 | W292: No newline at end |
| main.py:170,178 | E501: Line too long (95, 104 > 88) |
| orm_models.py:26,44 | E501: Line too long (113, 116 > 100) |

### Commented-Out Code (Intentional - Ignored)

main.py contains ~20 lines of commented-out code for board CRUD endpoints. Per instructions, these are ignored.

---

## 2. Flake8 Findings

### Style Violations

| Category | Count |
|----------|-------|
| E266 (too many #) | 12 |
| E302 (wrong blanks) | 10 |
| E303 (too many blanks) | 4 |
| E501 (line too long) | 4 |
| W291 (trailing whitespace) | 4 |
| W292 (no newline) | 4 |
| W293 (whitespace blank) | 6 |

### Files Affected

- main.py: ~45 issues
- models.py: 4 issues
- orm_models.py: 4 issues
- service.py: 4 issues
- config.py: 2 issues

---

## 3. Pylint Findings

### High Priority Issues

| File | Issue | Severity |
|------|-------|----------|
| service.py:1 | W0611: Unused import Optional |
| main.py:68 | C0415: Import inside function (JSONResponse) |
| main.py:67 | W0613: Unused argument 'request' |
| main.py:90+ | W0707: Missing `raise ... from e` in except |

### Function Complexity

| File | Line | Issue |
|------|------|-------|
| storage.py:69 | R0913: Too many arguments (6/5) |
| storage.py:370 | R0913: Too many arguments (6/5) |
| storage.py:728 | R0913: Too many arguments (6/5) |
| service.py:113 | R0913: Too many arguments (6/5) |

### Missing Docstrings

- 8 classes across codebase
- 20+ functions/methods

---

## 4. MyPy Findings

### Type Errors (9 total)

| File | Issue | Severity |
|------|-------|----------|
| orm_models.py:7,20,36,49 | Invalid base class "Base" | MEDIUM |
| storage.py:496 | Incompatible type Sequence vs list | LOW |

**Note**: ORM models import `Base` from `db.py` but mypy cannot resolve it. This is a False Positive for SQLAlchemy.

---

## 5. Bandit Findings

**No security issues found.** ✅

---

## 6. Manual Code Review

### Code Pattern Analysis

#### Duplicate Code Patterns

| Location | Pattern | Description |
|----------|---------|-------------|
| storage.py | `_to_kanban_data` x 2 | JsonStorage and SqlAlchemyStorage both have similar conversion logic |
| service.py | Exception raising | All use string literals instead of variables |

#### Inconsistent Patterns

| Area | Issue |
|------|-------|
| Exception handling | service.py uses string literals, should use variables (EM101) |
| Comments | main.py uses inconsistent block comment style (## vs ####) |
| Type hints | Some use Optional, others use `X \| None` (models.py) |

#### Developer Attribution

Based on patterns:
- **config.py, cli.py**: Clean code, good structure - likely one developer
- **main.py**: Inconsistent formatting (whitespace) - different developer
- **storage.py**: Complex functions with many args - experienced developer
- **models.py**: Clean dataclasses - modern Python approach
- **orm_models.py**: Traditional SQLAlchemy - older approach

---

## 7. Architectural Concerns

### Issues Identified

| Issue | Location | Severity |
|-------|----------|----------|
| Global variables | db.py:19 | HIGH |
| Import inside function | main.py:68 | MEDIUM |
| Too many arguments | storage.py, service.py | MEDIUM |
| Missing return type hints | Many functions | LOW |
| Circular import risk | main.py:68 imports in handler | LOW |

### Design Patterns

| Pattern | Implementation | Status |
|---------|--------------|--------|
| Strategy | StorageInterface | ✅ Good |
| Dataclass models | models.py | ✅ Good |
| ORM | orm_models.py | ✅ Good |
| Service Layer | service.py | ✅ Good |

---

## 8. Dead Code Detection

### Tool-Detected

- Service layer Optional import
- Unused `request` argument in exception handler

### Manual Review

- No truly dead code found
- Commented code is intentional (board CRUD endpoints)

---

## Priority Fix List

### High Priority (Fix Now)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 1 | Remove unused Optional import | service.py | Remove import |
| 2 | Add newline to files missing EOL | config.py, main.py, models.py, orm_models.py, service.py | Add newline |
| 3 | Fix trailing whitespace | main.py, models.py | Clean whitespace |

### Medium Priority (Fix Soon)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 4 | Add type hints to functions | main.py, service.py | Add return types |
| 5 | Add docstrings | All public functions | Add docstrings |
| 6 | Fix import inside function | main.py:68 | Move to top-level |
| 7 | Add raise-from in except | main.py:90+ | Add `from e` |

### Low Priority (Nice to Have)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 8 | Shorten long lines | storage.py, main.py | Reflow |
| 9 | Standardize comments | main.py | Use consistent style |
| 10 | Fix Optional vs None | models.py | Use `X \| None` |

---

## Recommendations

### Quick Wins (~15 minutes)

```bash
# Auto-fix with ruff
ruff check src/ --fix
```

### Refactoring Roadmap

1. **Week 1**: Fix high priority issues (whitespace, imports)
2. **Week 2**: Add type hints and docstrings
3. **Week 3**: Code complexity refactoring
4. **Week 4**: Full linting pass

---

## Files Analyzed

| File | Issues | Complexity |
|------|--------|------------|
| config.py | 2 | Low |
| cli.py | 5 | Low |
| db.py | 8 | Low |
| main.py | ~80 | Medium |
| models.py | 15 | Low |
| orm_models.py | 12 | Low |
| service.py | ~30 | Medium |
| storage.py | ~50 | High |

**Total lines of code**: ~1,080

---

*Generated: 2026-04-22*