# Architecture Review Plan Template

## Purpose
Create a reusable plan for conducting an architecture code review of a Python backend codebase.

---

## Pre-Review Research (Required First)

### 1. Explore Documentation
Review any existing documentation to understand prior work:
- **Docs directory**: Look for existing review documents (code-quality-review.md, code-review.md)
- **Architecture Decision Records (ADRs)**: docs/decisions/[0-9]*_*.md
- **Software Design Documents**: software-design-document.md

### 2. Review Prior Analysis
- **oc-changes/**: Check for previous inspection logs (code-inspection.log, test-results.log)
- **Archive docs/**: Check docs/archive/ for historical context

### 3. Understand Codebase Structure
Use glob to identify source files:
```bash
# For Python
glob pattern: **/src/**/*.py

# For other languages
# Adjust accordingly
```

---

## Architecture Review Phases

### Phase 1: Architectural Pattern Analysis

| Task | Approach | Deliverable |
|------|----------|-------------|
| Identify architectural pattern | Read main modules (main.py, app.py) | Layered/Hexagonal/MVC classification |
| Evaluate abstraction layers | Review service, storage, factory patterns | Layer value assessment |
| Check dependency management | Static analysis | Coupling diagram |
| Review SOLID principles | Manual code review | SRP/OCP violation list |

**Key questions**:
- Do layers add value or create unnecessary indirection?
- Is the service layer thin (pass-through) or does it contain real business logic?
- Are abstractions justified or over-engineered?

---

### Phase 2: Security Review

| Task | Approach | Deliverable |
|------|----------|-------------|
| Authentication model | Review ADRs, auth modules | Authentication strategy |
| Password/storage security | Review models, orm_models | Password handling assessment |
| API authorization | Review endpoints | Authorization gaps |
| Input sanitization | Review validation layers | Security vulnerability list |

**Standards to compare against**:
- OWASP Top 10
- Python security best practices
- Password hashing (bcrypt/argon2)

---

### Phase 3: Data Layer & Persistence

| Task | Approach | Deliverable |
|------|----------|-------------|
| Storage pattern analysis | Review storage.py, dao.py | Pattern classification |
| ID generation approach | Review ID generation logic | Concurrency risks |
| Database abstraction | Review ORM usage | Pattern effectiveness |
| Transaction handling | Review commits, rollbacks | Data integrity assessment |

**Key concerns**:
- Race conditions in ID generation
- Concurrent access safety
- Transaction boundaries

---

### Phase 4: API Design Maturity

| Task | Approach | Deliverable |
|------|----------|-------------|
| REST compliance | Review endpoints | REST maturity level |
| Input validation | Review Pydantic/validation layers | Validation gaps |
| Error handling | Review exception handlers | Consistency assessment |
| Response patterns | Review HTTP responses | Best practice compliance |

**Standards**:
- RFC 7807 (Problem Details for HTTP APIs)
- RESTful maturity levels (Richardson)
- JSON:API conventions

---

### Phase 5: Testing & Operations

| Task | Approach | Deliverable |
|------|----------|-------------|
| Test coverage gaps | Compare test files to code | Coverage holes |
| Configuration management | Review config.py | 12-factor compliance |
| Logging/monitoring | Source review | Observability assessment |
| Error handling | Review exception patterns | Error handling maturity |

---

### Phase 6: Code Quality & Best Practices

| Task | Tool | Target |
|------|------|--------|
| Linting | ruff, flake8, pylint | Style/format issues |
| Type checking | mypy | Type safety |
| Security scanning | bandit | Vulnerabilities |
| Complexity analysis | pylint, radon | Code complexity |

---

### Phase 7: Best Practice Comparison

Compare against established standards:
- **Language**: PEP 8, modern Python (type hints, dataclasses)
- **Framework**: FastAPI/SQLAlchemy best practices
- **Architecture**: Domain-driven design, clean architecture
- **Operations**: 12-factor app, containerization

---

## Review Deliverables

### 1. Architecture Issues Report
| Severity | Category | Issue | Location | Recommendation |
|----------|----------|-------|----------|--------------|
| CRITICAL | Security | ... | ... | ... |
| HIGH | Architecture | ... | ... | ... |

### 2. Best Practice Comparison
Document gaps against:
- Language standards
- Framework conventions
- Industry patterns

### 3. Prioritized Improvement List
Rank by:
- Security impact
- Technical debt
- Maintainability

---

## Notes
- **Scope**: Only identify problems, NOT fix them
- **Focus**: Compare to established best practices
- **Output**: Detailed report with severity and recommendations