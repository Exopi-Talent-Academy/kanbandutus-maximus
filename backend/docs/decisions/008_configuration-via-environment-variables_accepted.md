# ADR 008: Configuration via Environment Variables

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