# ADR 006: Data Validation

### Status
Accepted

### Decision
Use Pydantic for request/response validation.

### Goal
Ensure type safety and validation at API boundaries.

### Context
FastAPI has built-in Pydantic support. Need to validate incoming requests and serialize responses.

### Alternatives
- Manual validation: Error-prone, verbose
- Cerberus: Less common in FastAPI ecosystem

### Trade-offs
**Pros:** Built into FastAPI, type hints, automatic OpenAPI generation
**Cons:** Runtime validation overhead (minimal)