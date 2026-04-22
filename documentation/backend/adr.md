# Architecture Decision Record - Backend

## ADR 001: Backend Framework

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

---

## ADR 002: ORM Strategy

### Status
Accepted

### Decision
Use SQLAlchemy as the ORM layer.

### Goal
Provide database abstraction and enable switching between storage backends.

### Context
Project requirements include supporting both JSON file storage and database storage. Need a mature ORM that supports multiple database backends, since do not know the final requirements on the database system.

### Alternatives
- NoSQL Systems: Promises fast responses but this was unneeded; also no developer had experience wit them.
- Raw SQL: No abstraction, harder to maintain

### Trade-offs
**Pros:** Mature, supports multiple databases, flexible, SQLAlchemy 2.0 has good type support
**Cons:** None

---

## ADR 003: Default Storage Backend

### Status
Accepted

### Decision
Use SQLite as the default database storage.

### Goal
Provide a zero-configuration database for development and production use.

### Context
Need persistent storage. SQLite requires no setup and works well for single-user applications.

### Alternatives
- PostgreSQL: Requires setup, overkill for MVP
- JSON file: Simple but no query capability

### Trade-offs
**Pros:** Zero configuration, file-based, good performance for single user
**Cons:** Not suitable for high concurrent writes, limited to single-user by design

---

## ADR 004: Storage Abstraction

### Status
Accepted

### Decision
Use the Strategy pattern to abstract storage implementations.

### Goal
Enable pluggable storage backends (JSON file, SQLite, PostgreSQL) without changing service layer code.

### Context
Architecture that supports multiple storage types for several reasons:
1: Requirements specify JSON file storage as an option for testing purposes.
2: Stakeholder requirements might change and different database systems might be required in order to meet those requirements.


### Alternatives
- Factory pattern: More complex than needed
- Repository pattern: Similar but different naming

### Trade-offs
**Pros:** Easy to add new storage backends, decouples business logic from storage
**Cons:** Some interface overhead

---

## ADR 005: Data Validation

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

---

## ADR 006: Error Response Format

### Status
Accepted

### Decision
Use RFC 7807 Problem Details for HTTP API errors.

### Goal
Provide consistent, machine-readable error responses.

### Context
Need standardized error format for API clients to parse.

### Alternatives
- Custom JSON: Inconsistent
- XML errors: Less common
- Status code only: Not informative enough

### Trade-offs
**Pros:** Standard format understood by Angular, machine-readable, includes detail
**Cons:** Slightly more verbose

---

## ADR 007: Configuration via Environment Variables

### Status
Accepted

### Decision
Configure application via environment variables.

### Goal
Enable configuration without code changes for different environments.

### Context
Need way to configure storage backend, database path, and CORS origins.

### Alternatives
- Config file: More complex
- Hard-coded: Not flexible
- Database config: Would add dependency

### Trade-offs
**Pros:** Standard practice, easy to change
**Cons:** Need to document available variables

---

## ADR 008: No Authentication

### Status
Accepted

### Goal
Focus on core Kanban functionality without authentication complexity.

### Context
The MVP focuses on core Kanban functionality. Authentication adds significant complexity and is not required for initial development and testing.

### Decision
Skip authentication entirely for current product.

### Alternatives
- Basic auth: Adds complexity, requires user management
- JWT tokens: Requires user management, adds state
- Session-based: Requires database, adds complexity

### Trade-offs
**Pros:** Faster development, simpler architecture, easier testing
**Cons:** Anyone can modify any data, no user isolation, not suitable for production

---

## ADR 009: Auto-integer ID Generation

### Status
Accepted

### Goal
Provide simple, URL-friendly entity identifiers.

### Context
Entities need unique identifiers for API references and relationships.

### Decision
Use auto-incrementing integers for entity IDs, generated by finding the maximum existing ID.
This is good enough for now and easy to understand.
Later versions will likely need UUID identifiers.

### Alternatives
- UUID: Better for distributed systems, but longer URLs
- Custom: More work, no benefit

### Trade-offs
**Pros:** Simple implementation, URL-friendly, easy to understand, human-readable
**Cons:** Predictable IDs, race conditions with concurrent creates, limited scalability