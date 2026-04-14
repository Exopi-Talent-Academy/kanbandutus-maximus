# Architecture Diagram

```mermaid
flowchart TB
    subgraph API["FastAPI Application Layer"]
        main["main.py<br/>API Routes"]
    end
    
    subgraph Business["Business Logic Layer"]
        service["KanbanService<br/>service.py"]
    end
    
    subgraph Data["Data Layer"]
        storageI["StorageInterface<br/>storage.py"]
        json["JsonStorage<br/>storage.py"]
    end
    
    subgraph Models["Domain Models"]
        board["Board<br/>models.py"]
        column["Column<br/>models.py"]
        task["Task<br/>models.py"]
    end
    
    subgraph External["External"]
        frontend["FrontendInterface<br/>frontend.py"]
        jsonFile["kanban.json"]
    end
    
    API --> service
    service --> storageI
    storageI <--> json
    json <--> jsonFile
    
    service --> board
    service --> column
    service --> task
    
    main --> frontend
    
    style API fill:#e1f5fe
    style Business fill:#fff3e0
    style Data fill:#e8f5e9
    style Models fill:#fce4ec
    style External fill:#f5f5f5
```

## Component Overview

- **main.py**: FastAPI routes handling HTTP requests/responses
- **service.py**: Business logic layer (KanbanService)
- **storage.py**: Data persistence (StorageInterface + JsonStorage)
- **models.py**: Domain models (Board, Column, Task)
- **frontend.py**: Frontend interface abstraction
- **config.py**: Configuration (data file paths)