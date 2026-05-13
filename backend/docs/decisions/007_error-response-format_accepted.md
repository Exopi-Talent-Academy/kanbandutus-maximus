# ADR 007: Error Response Format

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

### Note
Supersedes ADR-004 from local implementation.