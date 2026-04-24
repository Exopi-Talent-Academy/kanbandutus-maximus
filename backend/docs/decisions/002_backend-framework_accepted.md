# ADR 002: Backend Framework

### Status
Accepted

### Decision
Use FastAPI as the backend framework.
In addition to the requirements it also provided automatic OpenAPI documentation.
Also had Pydantic available for request validation at API interface level.

### Goal
Provide a lightweight, high-performance REST API for the Kanban application.

### Context
Need a Python web framework that supports quick development, a testable interface, and easy integration with Angular frontend.

### Alternatives
- Flask: Lighter but requires more manual setup for API features
- Django: Full-featured but probably overkill for this use case

### Trade-offs
**Pros:** Built-in OpenAPI/Swagger docs, async support, Pydantic integration, type hints
**Cons:** Newer framework, smaller ecosystem than Flask/Django