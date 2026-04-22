# Code Quality Review Instructions

Instructions for performing a comprehensive code quality review of the Kanban backend.

---

## Overview

This document provides step-by-step instructions for another agent (or future self) to perform a code quality review using static analysis tools.

**Goal**: Identify code issues, architectural concerns, and code smells in the implementation.

**Scope**: Focus on `src/` directory only.

---

## Prerequisites

### 1. Activate Virtual Environment

```bash
source virtual-environment-kanban/bin/activate
```

### 2. Install Linters

If linters are not installed:

```bash
pip install ruff pylint mypy bandit flake8
```

Or install from project dependencies:

```bash
pip install -e ".[dev]"
```

Verify installation:

```bash
ruff --version
pylint --version
mypy --version
bandit --version
flake8 --version
```

---

## Execution Steps

### Step 1: Run All Linters

Run each tool and save results:

```bash
# Ruff: Fast linting and style
ruff check src/ --select=ALL > docs/ruff_findings.txt

# Flake8: Style enforcement
flake8 src/ --max-line-length=100 > docs/flake8_findings.txt

# Pylint: Deep code quality
pylint src/kanban/ --disable=C0114,C0116 --max-line-length=100 > docs/pylint_findings.txt

# MyPy: Type checking
mypy src/ > docs/mypy_findings.txt

# Bandit: Security vulnerabilities
bandit -r src/ > docs/bandit_findings.txt
```

### Step 2: Review Tool Outputs

Read each findings file and categorize issues:

| Severity Level | Criteria |
|---------------|----------|
| **Critical** | Security vulnerabilities, data loss risk |
| **High** | Unused imports, broken imports, syntax errors |
| **Medium** | Missing type hints, missing docstrings, complexity |
| **Low/Style** | Whitespace, line length, formatting |

### Step 3: Manual Code Review

1. **Read each source file** (`src/kanban/*.py`)
2. **Identify patterns**:
   - Duplicate code patterns
   - Inconsistent naming
   - Developer attribution (different coding styles)
3. **Check architectural concerns**:
   - Layer separation (Storage → Service → API)
   - Design patterns in use
   - Error handling consistency

### Step 4: Create Documentation

Create `docs/code-quality-review.md` with sections:

1. **Summary**: Table of tool results
2. **Tool Findings**: Details from each linter
3. **Manual Review**: Patterns and attribution
4. **Architectural Concerns**: Design issues
5. **Priority Fix List**: What to fix first
6. **Recommendations**: Roadmap for improvements

---

## Document Template

Use this template when creating the review document:

```markdown
# Code Quality Review

**Date**: YYYY-MM-DD
**Scope**: src/

---

## Tools Used

| Tool | Purpose | Issues Found |
|------|---------|-------------|
| ruff | Fast linting | N |
| flake8 | Style | N |
| pylint | Quality | N |
| mypy | Types | N |
| bandit | Security | N |

---

## Summary

| Category | Issues |
|----------|--------|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |

---

## 1. Ruff Findings

### Fixable Issues (* = auto-fixable)

[List fixable issues]

### Docstring Issues

[List missing docstrings]

### Style Issues

[List style violations]

---

## 2. Flake8 Findings

### By Category

| Category | Count |
|----------|-------|
| E2xx | N |
| W2xx | N |
| ... | ... |

### Files Affected

| File | Count |
|------|-------|
| main.py | N |
| ... | ... |

---

## 3. Pylint Findings

### High Priority Issues

[List critical issues]

### Function Complexity

[List functions with R0913/R0917]

---

## 4. MyPy Findings

### Type Errors

[List type checking errors]

---

## 5. Bandit Findings

### Security Issues

[List security vulnerabilities - should be empty]

---

## 6. Manual Code Review

### Code Pattern Analysis

[Patterns identified across files]

### Developer Attribution

[Notes on different coding styles]

---

## 7. Architectural Concerns

| Issue | Location | Severity | Fix |
|-------|----------|----------|-----|
| ... | ... | ... | ... |

---

## 8. Dead Code Detection

### Tool-Detected

[List unused code found by tools]

### Manual Review

[List any truly dead code found]

---

## Priority Fix List

### High Priority (Fix Now)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 1 | ... | ... | ... |

### Medium Priority (Fix Soon)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 1 | ... | ... | ... |

### Low Priority (Nice to Have)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 1 | ... | ... | ... |

---

## Recommendations

1. **Quick fixes**: Run `ruff check src/ --fix`
2. **Short-term**: Add type hints and docstrings
3. **Long-term**: Refactor complex functions

---

## Files Analyzed

| File | Issues | Complexity |
|------|--------|------------|
| config.py | N | Low/Medium/High |
| cli.py | N | Low/Medium/High |
| db.py | N | Low/Medium/High |
| main.py | N | Low/Medium/High |
| models.py | N | Low/Medium/High |
| orm_models.py | N | Low/Medium/High |
| service.py | N | Low/Medium/High |
| storage.py | N | Low/Medium/High |

**Total lines of code**: ~N

---

*Generated: YYYY-MM-DD*
```

---

## Key Notes for Agent

1. **Scope**: Always focus on `src/` only (tests excluded per instructions)
2. **Commented endpoints**: Ignore - they are intentionally commented out, not dead code
3. **False positives**: MyPy often reports false positives for SQLAlchemy - note but don't flag as issues
4. **Security**: Bandit should find ZERO issues - if it does, flag as Critical
5. **Duplicates**: Look for duplicate code patterns between storage implementations

---

## Quick Reference Commands

```bash
# Full review
ruff check src/ --select=ALL > ruff.txt
flake8 src/ --max-line-length=100 > flake8.txt
pylint src/kanban/ --disable=C0114,C0116 --max-line-length=100 > pylint.txt
mypy src/ > mypy.txt
bandit -r src/ > bandit.txt

# Quick fix (auto-fixable issues only)
ruff check src/ --fix

# Count issues
wc -l *.txt
```

---

*Last updated: 2026-04-22*