"""
FastAPI application for the Kanban Board API.

This module defines the REST API endpoints, request/response models,
and middleware configuration for the Kanban backend.

The API follows these principles:
- RFC 7807 error responses for consistent error formatting
- Pydantic validation for all request bodies
- DTO-based responses for API stability
- Role-based access control for write operations
"""

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_storage_config, get_cors_origins
from .dto import AccountResponse
from .repositories import KanbanStorage
from .service import KanbanService, NotFoundError
from .storage import JsonStorage, SqlAlchemyStorage

app = FastAPI(title="Kanban API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_storage():
    """
    Create and return a storage instance based on configuration.

    Returns:
        A storage implementation (JsonStorage or SqlAlchemyStorage)
    """
    config = get_storage_config()
    if config.backend == "sqlite":
        return SqlAlchemyStorage()
    return JsonStorage(config.json_file)


service = KanbanService(get_storage())


WRITE_ROLES = {"admin", "write"}


def get_current_demo_account(
    x_demo_account_id: str | None = Header(default=None, alias="X-Demo-Account-Id"),
) -> dict:
    """
    Extract and validate the current account from request headers.

    Args:
        x_demo_account_id: Account ID passed via X-Demo-Account-Id header

    Returns:
        Account data as a dictionary

    Raises:
        HTTPException: If header is missing, invalid, or account not found
    """
    if x_demo_account_id is None:
        raise HTTPException(status_code=401, detail="Missing X-Demo-Account-Id header")

    try:
        account_id = int(x_demo_account_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="X-Demo-Account-Id must be an integer"
        ) from exc

    try:
        return service.get_account_dto(account_id).model_dump()
    except NotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def require_write_access(
    current_account: dict = Depends(get_current_demo_account),
) -> dict:
    """
    Require that the current account has write access.

    Args:
        current_account: The authenticated account from the header

    Returns:
        The account data if write access is granted

    Raises:
        HTTPException: If account lacks write access
    """
    role = current_account.get("role", "read")
    if role not in WRITE_ROLES:
        username = current_account.get("username", "unknown")
        raise HTTPException(
            status_code=403,
            detail=f"Account '{username}' does not have write access",
        )
    return current_account


@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc: NotFoundError):
    """
    Global exception handler for NotFoundError exceptions.

    Returns RFC 7807 formatted error response.
    """
    return JSONResponse(
        status_code=404,
        content={
            "type": f"https://api.example.com/errors/{exc.entity.lower()}-not-found",
            "title": f"{exc.entity} Not Found",
            "status": 404,
            "detail": str(exc),
        },
    )


##### BOARDS #####


@app.get("/api/boards")
def get_boards():
    """
    Get all boards.

    Returns:
        List of all boards with their columns and tasks
    """
    return service.get_all_boards_dto()


@app.get("/api/boards/{board_id}")
def get_board(board_id: int):
    """
    Get a single board by ID.

    Args:
        board_id: The ID of the board to retrieve

    Returns:
        The board with all columns and tasks
    """
    return service.get_board_dto(board_id)


# Board CRUD endpoints - commented out (not yet implemented)
# @app.post("/api/boards")
# def create_board(board: BoardCreate):
#     return service.create_board_dto(board.name)
#
# @app.put("/api/boards/{board_id}")
# def update_board(board_id: int, board: BoardUpdate):
#     return service.update_board_dto(board_id, board.name)
#
# @app.delete("/api/boards/{board_id}")
# def delete_board(board_id: int):
#     service.delete_board(board_id)
#     return {"message": "Board deleted"}


# Column listing endpoint - commented out (use board endpoint instead)
# @app.get("/api/boards/{board_id}/columns")
# def get_columns(board_id: int):
#     return service.get_columns_by_board(board_id)


##### COLUMNS #####


@app.post("/api/columns")
def create_column(column: dict, current_account: dict = Depends(require_write_access)):
    """
    Create a new column within a board.

    Args:
        column: Column data including name, position, and board_id
        current_account: The authenticated account with write access

    Returns:
        The newly created column
    """
    return service.create_column_dto(
        column["name"], column["position"], column["board_id"]
    )


@app.put("/api/columns/{column_id}")
def update_column(
    column_id: int, column: dict, current_account: dict = Depends(require_write_access)
):
    """
    Update a column's name and/or position.

    Args:
        column_id: The ID of the column to update
        column: Updated column data including name and position
        current_account: The authenticated account with write access

    Returns:
        The updated column
    """
    return service.update_column_dto(column_id, column["name"], column["position"])


@app.delete("/api/columns/{column_id}")
def delete_column(
    column_id: int, current_account: dict = Depends(require_write_access)
):
    """
    Delete a column and all its tasks.

    Args:
        column_id: The ID of the column to delete
        current_account: The authenticated account with write access

    Returns:
        Confirmation message
    """
    service.delete_column(column_id)
    return {"message": "Column deleted"}


##### TASKS #####


@app.get("/api/columns/{column_id}/tasks")
def get_tasks(column_id: int):
    """
    Get all tasks belonging to a column.

    Args:
        column_id: The ID of the parent column

    Returns:
        List of tasks in the column
    """
    return service.get_tasks_by_column_dto(column_id)


@app.post("/api/tasks")
def create_task(task: dict, current_account: dict = Depends(require_write_access)):
    """
    Create a new task within a column.

    Args:
        task: Task data including title, description, column_id, and position
        current_account: The authenticated account with write access

    Returns:
        The newly created task
    """
    return service.create_task_dto(
        task["title"],
        task.get("description", ""),
        task["column_id"],
        task.get("position", 0),
    )


@app.put("/api/tasks/{task_id}")
def update_task(
    task_id: int, task: dict, current_account: dict = Depends(require_write_access)
):
    """
    Update a task's fields and/or move to a different column.

    Args:
        task_id: The ID of the task to update
        task: Updated task data
        current_account: The authenticated account with write access

    Returns:
        The updated task
    """
    return service.update_task_dto(
        task_id,
        task["title"],
        task["description"],
        task["column_id"],
        task["position"],
    )


@app.delete("/api/tasks/{task_id}", status_code=200)
def delete_task(task_id: int, current_account: dict = Depends(require_write_access)):
    """
    Delete a task by ID.

    Args:
        task_id: The ID of the task to delete
        current_account: The authenticated account with write access

    Returns:
        Confirmation message
    """
    service.delete_task(task_id)
    return {"message": "Task deleted"}


# Task retrieval endpoint - commented out (use board endpoint instead)
# @app.get("/api/tasks/{task_id}")
# def get_task(task_id: int):
#     return service.get_task_dto(task_id)


##### ACCOUNTS #####


@app.get("/api/accounts", response_model=list[AccountResponse])
def get_accounts() -> list[AccountResponse]:
    """
    Get all accounts.

    Returns:
        List of all accounts (excludes password_hash)
    """
    return service.get_all_accounts_dto()


@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int) -> AccountResponse:
    """
    Get a specific account by ID.

    Args:
        account_id: The ID of the account to retrieve

    Returns:
        The account data (excludes password_hash)
    """
    return service.get_account_dto(account_id)
