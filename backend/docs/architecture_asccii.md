# Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KANBAN APPLICATION       │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   REST API       │
                              │   (FastAPI)      │
                              │   main.py        │
                              └────────┬─────────┘
                                       │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
           │ BoardCreate  │  │ ColumnCreate│  │  TaskCreate │
           │ BoardUpdate │  │ ColumnUpdate│  │  TaskUpdate │
           │ Pydantic     │  │ Pydantic    │  │  Pydantic   │
           └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                  │                │                │
                  └────────────────┼────────────────┘
                                   ▼
                        ┌─────────────────────┐
                        │   SERVICE LAYER    │
                        │   service.py       │
                        │   KanbanService   │
                        │   - get_board()  │
                        │   - create_*()  │
                        │   - update_*()  │
                        │   - delete_*()  │
                        └────────┬────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │   STORAGE ABSTRACTION│
                    │   storage.py        │
                    │   StorageInterface │
                    │   (ABC)            │
                    └────────┬───────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │   PERSISTENCE         │
                    │   JsonStorage       │
                    │   - load/save       │
                    │   - CRUD operations│
                    └────────┬───────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │   data.json         │
                    │   (file)            │
                    └───────────��──────────┘

─────────────────────────────────────────────────────────────────────────────

                        ┌────────────────────┐
                        │   DOMAIN MODELS    │
                        │   models.py       │
                        └────────────────────┘
                        
         ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌────────────┐
         │  Board   │    │  Column   │    │   Task   │    │KanbanData │
         │ - id     │    │ - id      │    │ - id     │    │- boards  │
         │ - name   │    │ - name    │    │ - title │    │- columns │
         │ - cols   │    │ - pos     │    │ - desc  │    │- tasks   │
         └──────────┘    │ - board_id     │    │ - col_id│    │          │
                         │ - position     │    │ - pos  │    │+ helpers │
                         └───────────┘    └──────────┘    └────────────┘

─────────────────────────────────────────────────────────────────────────────

                         EXTERNAL DEPENDENCIES
                         ─────────────────
                         - FastAPI (API framework)
                         - Pydantic (validation)
                         - json (built-in)
                         - pathlib (built-in)
```