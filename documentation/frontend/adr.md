# Architecture Decision Record - Frontend

## ADR 001: Frontend Framework

### Status
Accepted

### Decision
Use Angular as the frontend framework.

### Goal
Build a Single Page Application (SPA) for the Kanban board with a component-based architecture.

### Context
We are a small team required to develop an application from scratch at speed.
Angular is a standard frontend, and the frontend developer is familiar with it.

### Alternatives
- React: Popular but less opinionated, more configuration and less developer familiarity
- Vue: Simpler but smaller ecosystem
- Vanilla: Too much boilerplate needed

### Trade-offs
**Pros:** Opinionated structure, good for large apps, TypeScript-native, strong tooling
**Cons:** Steeper learning curve, more verbose than React/Vue

---

## ADR 002: State Management

### Status
Accepted

### Decision
Use Angular Signals for reactive state management.

### Goal
Manage application state (board data, task updates) with modern Angular primitives.

### Context
Angular 19 provides Signals for reactive state. Need to manage board data and reflect API changes.

### Alternatives
- RxJS subjects: More complex, harder to learn
- NgRx: Heavy for this use case
- Service with BehaviorSubject: Works but Signals are cleaner

### Trade-offs
**Pros:** Simple API, built into Angular 19, automatic change detection
**Cons:** Newer, less community examples

---

## ADR 003: HTTP Communication

### Status
Accepted

### Decision
Use Angular HttpClient for API communication.

### Goal
Communicate with FastAPI backend via HTTP.

### Context
Backend exposes REST API. Frontend needs to fetch, create, update, and delete tasks.

### Alternatives
- Fetch API: More verbose, no interceptor support
- Axios: Extra dependency
- WebSocket: Not needed for this use case

### Trade-offs
**Pros:** Built into Angular, supports interceptors, typed responses
**Cons:** None significant

---

## ADR 004: Component Architecture

### Status
Accepted

### Decision
Nested component hierarchy: Board > EachColumn > EachRow > Task.

### Goal
Create reusable components following Angular best practices.

### Context
Need to display boards, columns, and tasks. Each level should be reusable and maintainable.

### Alternatives
- Flat components: Harder to maintain, less reusable
- Single page: Not feasible for complexity
- Multiple routes: Not a single-board app

### Trade-offs
**Pros:** Reusable, maintainable, clear data flow
**Cons:** More files to manage

---

## ADR 005: Styling Approach

### Status
Accepted

### Decision
Use Tailwind CSS for styling.

### Goal
Provide rapid styling without writing custom CSS.

### Context
Requirements specify Tailwind. Need utility-first approach for quick development.

### Alternatives
- Custom CSS: More work, harder to maintain
- SCSS: Requires setup
- Angular Material: Too heavy, not needed

### Trade-offs
**Pros:** Fast development, consistent design, small bundle
**Cons:** Class names can get long, learning curve

---

## ADR 006: Drag and Drop

### Status
Accepted

### Decision
Use Angular CDK Drag and Drop for task movement.

### Goal
Enable intuitive drag-and-drop task reordering between columns.

### Context
Kanban boards require moving tasks between columns. Need smooth drag-and-drop experience.

### Alternatives
- Native HTML5 DnD: Limited, inconsistent
- Third-party libs: Extra dependencies
- Buttons only: Less intuitive

### Trade-offs
**Pros:** Built into Angular CDK, smooth animations, good accessibility
**Cons:** Need Angular CDK dependency

---

## ADR 007: Form Handling

### Status
Accepted

### Decision
Use template-driven forms with local component state.

### Goal
Handle task creation and editing with minimal boilerplate.

### Context
Tasks can be created and edited. Need simple form handling.

### Alternatives
- Reactive forms: More boilerplate for simple use case
- Plain inputs: Less Angular-idiomatic
- Modal dialogs: More complex

### Trade-offs
**Pros:** Simple, minimal code, easy to understand
**Cons:** Less validation control

---

## ADR 008: TypeScript for Type Safety

### Status
Accepted

### Decision
Use TypeScript interfaces matching backend API.

### Goal
Ensure type consistency between frontend and backend.

### Context
Backend uses Pydantic models. Frontend should have matching TypeScript interfaces.

### Decision
Define TypeScript interfaces that mirror backend Pydantic models.

### Alternatives
- any types: Error-prone
- Dynamic typing: Loses benefits
- Generated types: More setup

### Trade-offs
**Pros:** Catches errors at compile time, self-documenting, refactor-safe
**Cons:** Need to keep in sync manually