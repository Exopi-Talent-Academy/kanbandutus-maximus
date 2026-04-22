# ADR 003: ORM Strategy

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