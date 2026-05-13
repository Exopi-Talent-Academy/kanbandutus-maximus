# ADR 009: No Authentication

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