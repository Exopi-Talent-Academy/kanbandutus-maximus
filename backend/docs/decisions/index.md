# Architecture Decision Records - Index

This directory contains the architectural decision records (ADRs) for the Kanban backend project.

Each record follows the format: `{number}_{title}_{status}.md`

## Table of Contents

| # | Title | Status |
|---|-------|--------|
| 001 | Backend Development Language | Accepted |
| 002 | Backend Framework | Accepted |
| 003 | ORM Strategy | Accepted |
| 004 | Default Storage Backend | Accepted |
| 005 | Storage Abstraction | Accepted |
| 006 | Data Validation | Accepted |
| 007 | Error Response Format | Accepted |
| 008 | Configuration via Environment Variables | Accepted |
| 009 | No Authentication | Accepted |
| 010 | Auto-integer ID Generation | Accepted |
| 011 | Storage Configuration Consolidation | Accepted |

## Overview

### Technology Stack Decisions
- **001**: Python as the development language
- **002**: FastAPI as the web framework
- **003**: SQLAlchemy as the ORM layer

### Storage Decisions
- **004**: SQLite as default storage
- **005**: Strategy pattern for storage abstraction (JSON + SQLite backends)
- **011**: Consolidated storage configuration with StorageConfig

### API Design Decisions
- **006**: Pydantic for request/response validation
- **007**: RFC 7807 Problem Details for error responses
- **008**: Configuration via environment variables

### Security & Identification
- **009**: No authentication (MVP)
- **010**: Auto-integer ID generation

## Adding New Records

When adding a new ADR:
1. Create a new file with the format: `{number}_{title-snake-case}_{status}.md`
2. Include the ADR number, title, status, goal, context, decision, alternatives, and trade-offs
3. Update this index with the new record

## References

- Original source: `~/solo/repositories/public/kanban/kanban-documentation/documentation/backend/adr.md`
- ADR format inspired by [Michael Nygard's approach](https://cognitect.com/blog/2021/4/6/documenting-architecture-decisions)