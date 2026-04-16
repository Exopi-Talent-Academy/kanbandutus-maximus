# API Documentation

## Overview

The Kanban Board API is a REST API service that provides endpoints for managing Kanban boards, columns, and tasks. It is built with FastAPI and uses JSON file storage.

**Base URL:** `http://localhost:8000`  
**Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

**Status:** Not implemented

This API does not currently support authentication. All endpoints are publicly accessible.

---

## Rate Limiting

**Status:** Not implemented

---

## Error Handling

### Error Response Format (RFC 7807)

All error responses follow this format:

```json
{
  "type": "https://api.example.com/errors/{error-type}",
  "title": "Human-readable error title",
  "status": 404,
  "detail": "Detailed error message"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Resource not found |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

---

## Boards

### List Boards

Returns all boards.

**Endpoint:** `GET /api/boards`

**Parameters:** None

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "My Board",
    "columns": [1, 2, 3]
  }
]
```

---

### Get Board

Returns a specific board by ID.

**Endpoint:** `GET /api/boards/{board_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| board_id | integer | path | Board ID |

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "My Board",
  "columns": [1, 2, 3]
}
```

**Error Response:** `404 Not Found`
```json
{
  "type": "https://api.example.com/errors/board-not-found",
  "title": "Board Not Found",
  "status": 404,
  "detail": "Board with id=999 not found"
}
```

---

### Create Board

Creates a new board. *(Not implemented)*

**Endpoint:** `POST /api/boards`

**Request Body:**
```json
{
  "name": "New Board"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "name": "New Board",
  "columns": []
}
```

---

### Update Board

Updates an existing board. *(Not implemented)*

**Endpoint:** `PUT /api/boards/{board_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| board_id | integer | path | Board ID |

**Request Body:**
```json
{
  "name": "Updated Board Name"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Updated Board Name",
  "columns": [1, 2, 3]
}
```

---

### Delete Board

Deletes a board and all its columns/tasks. *(Not implemented)*

**Endpoint:** `DELETE /api/boards/{board_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| board_id | integer | path | Board ID |

**Response:** `200 OK`
```json
{
  "message": "Board deleted"
}
```

---

## Columns

### Get Columns by Board

Returns all columns for a specific board. *(Not implemented)*

**Endpoint:** `GET /api/boards/{board_id}/columns`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| board_id | integer | path | Board ID |

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "To Do",
    "position": 0,
    "board_id": 1
  }
]
```

---

### Create Column

Creates a new column. *(Not implemented)*

**Endpoint:** `POST /api/columns`

**Request Body:**
```json
{
  "name": "New Column",
  "position": 0,
  "board_id": 1
}
```

**Response:** `201 Created`
```json
{
  "id": 4,
  "name": "New Column",
  "position": 0,
  "board_id": 1
}
```

---

### Update Column

Updates an existing column. *(Not implemented)*

**Endpoint:** `PUT /api/columns/{column_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| column_id | integer | path | Column ID |

**Request Body:**
```json
{
  "name": "Updated Column",
  "position": 1
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Updated Column",
  "position": 1,
  "board_id": 1
}
```

---

### Delete Column

Deletes a column and all its tasks. *(Not implemented)*

**Endpoint:** `DELETE /api/columns/{column_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| column_id | integer | path | Column ID |

**Response:** `200 OK`
```json
{
  "message": "Column deleted"
}
```

---

## Tasks

### Get Tasks by Column

Returns all tasks for a specific column. *(Not implemented)*

**Endpoint:** `GET /api/columns/{column_id}/tasks`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| column_id | integer | path | Column ID |

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Task 1",
    "description": "Description",
    "column_id": 1,
    "position": 0
  }
]
```

---

### Get Task

Returns a specific task by ID. *(Not implemented)*

**Endpoint:** `GET /api/tasks/{task_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| task_id | integer | path | Task ID |

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Task Title",
  "description": "Task description",
  "column_id": 1,
  "position": 0
}
```

---

### Create Task

Creates a new task.

**Endpoint:** `POST /api/tasks`

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description (optional)",
  "column_id": 1,
  "position": 0
}
```

**Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| title | string | Yes | - | Task title |
| description | string | No | "" | Task description |
| column_id | integer | Yes | - | Parent column ID |
| position | integer | No | 0 | Order within column |

**Response:** `201 Created`
```json
{
  "id": 2,
  "title": "New Task",
  "description": "Task description (optional)",
  "column_id": 1,
  "position": 0
}
```

**Error Response:** `404 Not Found` (if column_id doesn't exist)
```json
{
  "type": "https://api.example.com/errors/column-not-found",
  "title": "Column Not Found",
  "status": 404,
  "detail": "Column with id=999 not found"
}
```

---

### Update Task

Updates an existing task.

**Endpoint:** `PUT /api/tasks/{task_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| task_id | integer | path | Task ID |

**Request Body:**
```json
{
  "title": "Updated Task",
  "description": "Updated description",
  "column_id": 2,
  "position": 1
}
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title |
| description | string | Yes | Task description |
| column_id | integer | Yes | Target column ID |
| position | integer | Yes | Order within column |

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Updated Task",
  "description": "Updated description",
  "column_id": 2,
  "position": 1
}
```

**Error Response:** `404 Not Found`
```json
{
  "type": "https://api.example.com/errors/task-not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "Task with id=999 not found"
}
```

---

### Delete Task

Deletes a task. *(Not implemented)*

**Endpoint:** `DELETE /api/tasks/{task_id}`

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| task_id | integer | path | Task ID |

**Response:** `200 OK`
```json
{
  "message": "Task deleted"
}
```

---

## Data Types

### Board
```json
{
  "id": 1,
  "name": "My Board",
  "columns": [1, 2, 3]
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique board identifier |
| name | string | Board display name |
| columns | array[integer] | IDs of columns in this board |

### Column
```json
{
  "id": 1,
  "name": "To Do",
  "position": 0,
  "board_id": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique column identifier |
| name | string | Column display name |
| position | integer | Sort order within board |
| board_id | integer | Parent board ID |

### Task
```json
{
  "id": 1,
  "title": "Task Title",
  "description": "Task description",
  "column_id": 1,
  "position": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique task identifier |
| title | string | Task display title |
| description | string | Detailed task description |
| column_id | integer | Parent column ID |
| position | integer | Sort order within column |

---

## Example Usage

### cURL

#### List all boards
```bash
curl -X GET http://localhost:8000/api/boards
```

#### Create a task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "Do something", "column_id": 1, "position": 0}'
```

#### Update a task
```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task", "description": "Done!", "column_id": 2, "position": 0}'
```

### Python

```python
import requests

# List boards
boards = requests.get("http://localhost:8000/api/boards").json()

# Create task
task = requests.post(
    "http://localhost:8000/api/tasks",
    json={"title": "New Task", "column_id": 1}
).json()

# Update task
updated = requests.put(
    f"http://localhost:8000/api/tasks/{task['id']}",
    json={"title": "Done", "description": "Completed", "column_id": 2, "position": 0}
).json()
```
