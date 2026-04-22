# ADR 001: Backend Development Language

### Status
Accepted

### Decision
Use Python as the backend development language.

### Goal
Build a backend quickly that can deliver a standard REST API, preferably in a way that most of the team can understand and interact with.

### Context
We are a small team required to develop an application from scratch at speed.
Everyone on the team has read or interacted with Python before to some degree, and the backend developer is familiar with it.

### Alternatives
- C#: A lot of boilerplate for the purpose; less developer familiarity
- Javascript: Less language knowledge required, but team was overall equally or more familiar with Python.
- Go: Technically the better choice, but noone on the team were familiar with it. Should be considered if fast response times or heavy load becomes a factor.

### Trade-offs
**Pros:** Widely understood, flexible; solid frameworks available and widely supported.
**Cons:** Interpreted language, slower.