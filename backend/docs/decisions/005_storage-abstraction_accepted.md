# ADR 005: Storage Abstraction

### Status
Accepted

### Decision
Use the Strategy pattern to abstract storage implementations.

### Goal
Enable pluggable storage backends (JSON file, SQLite, PostgreSQL) without changing service layer code.

### Context
Architecture that supports multiple storage types for several reasons:
1. Requirements specify JSON file storage as an option for testing purposes.
2. Stakeholder requirements might change and different database systems might be required in order to meet those requirements.

### Alternatives
- Factory pattern: More complex than needed
- Repository pattern: Similar but different naming

### Trade-offs
**Pros:** Easy to add new storage backends, decouples business logic from storage
**Cons:** Some interface overhead