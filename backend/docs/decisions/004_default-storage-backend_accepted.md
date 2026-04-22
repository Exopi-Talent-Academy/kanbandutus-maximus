# ADR 004: Default Storage Backend

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