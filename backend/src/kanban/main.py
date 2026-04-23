from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import get_data_file, get_storage_backend, get_cors_origins
from .models import Account
from .service import KanbanService, NotFoundError
from .storage import JsonStorage, SqlAlchemyStorage, StorageInterface

app = FastAPI(title="Kanban API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_storage() -> StorageInterface:
    if get_storage_backend() == "sqlite":
        return SqlAlchemyStorage()
    return JsonStorage(get_data_file())


service = KanbanService(get_storage())


# Manual serializer helpers are no longer needed for board responses;
# FastAPI can encode nested dataclasses directly from service objects.


class BoardCreate(BaseModel):
    name: str


class BoardUpdate(BaseModel):
    name: str


class ColumnCreate(BaseModel):
    name: str
    position: int
    board_id: int


class ColumnUpdate(BaseModel):
    name: str
    position: int


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    column_id: int
    position: int = 0


class TaskUpdate(BaseModel):
    title: str
    description: str
    column_id: int
    position: int


class AccountResponse(BaseModel):
    id: int
    username: str
    role: str


WRITE_ROLES = {"admin", "write"}


def _serialize_account(account: Account) -> dict[str, int | str]:
    return {
        "id": account.id,
        "username": account.username,
        "role": account.role,
    }


def get_current_demo_account(x_demo_account_id: str | None = Header(default=None, alias="X-Demo-Account-Id")) -> Account:
    if x_demo_account_id is None:
        raise HTTPException(status_code=401, detail="Missing X-Demo-Account-Id header")

    try:
        account_id = int(x_demo_account_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-Demo-Account-Id must be an integer") from exc

    try:
        return service.get_account(account_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def require_write_access(current_account: Account = Depends(get_current_demo_account)) -> Account:
    if current_account.role not in WRITE_ROLES:
        raise HTTPException(status_code=403, detail=f"Account '{current_account.username}' does not have write access")
    return current_account


@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc: NotFoundError):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"type": f"https://api.example.com/errors/{exc.entity.lower()}-not-found",
                 "title": f"{exc.entity} Not Found",
                 "status": 404,
                 "detail": str(exc)}
    )
    
    
##### BOARDS #####

# Gets the board for display
@app.get("/api/boards")
def get_boards():
    return service.get_all_boards()

@app.get("/api/boards/{board_id}")
def get_board(board_id: int):
    try:
        return service.get_board(board_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

## Creates a board
# @app.post("/api/boards")
# def create_board(board: BoardCreate):
#     return service.create_board(board.name)

## Updates board, for example, changing the the board title.
# @app.put("/api/boards/{board_id}")
# def update_board(board_id: int, board: BoardUpdate):
#     try:
#         return service.update_board(board_id, board.name)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))

## Deletes board.
# @app.delete("/api/boards/{board_id}")
# def delete_board(board_id: int):
#     try:
#         service.delete_board(board_id)
#         return {"message": "Board deleted"}
#     except NotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))


## Get Columns. We probably shouldn't use this (use Get Board instead)
# @app.get("/api/boards/{board_id}/columns")
# def get_columns(board_id: int):
#     try:
#         return service.get_columns_by_board(board_id)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))




##### COLUMNS #####

# Create new Column.
@app.post("/api/columns")
def create_column(column: ColumnCreate, current_account: Account = Depends(require_write_access)):
    try:
        return service.create_column(column.name, column.position, column.board_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Updates Column data (such as name, position)
@app.put("/api/columns/{column_id}")
def update_column(column_id: int, column: ColumnUpdate, current_account: Account = Depends(require_write_access)):
    try:
        return service.update_column(column_id, column.name, column.position)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Deletes a Column.  
@app.delete("/api/columns/{column_id}")
def delete_column(column_id: int, current_account: Account = Depends(require_write_access)):
    try:
        service.delete_column(column_id)
        return {"message": "Column deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))




##### TASKS #####

## Get task. We probably shouldn't use this (use Get Board instead).
@app.get("/api/columns/{column_id}/tasks")
def get_tasks(column_id: int):
    try:
        return service.get_tasks_by_column(column_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

## Creates new Task.
@app.post("/api/tasks")
def create_task(task: TaskCreate, current_account: Account = Depends(require_write_access)):
    try:
        return service.create_task(task.title, task.description, task.column_id, task.position)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

## Updates a task.
@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate, current_account: Account = Depends(require_write_access)):
    try:
        return service.update_task(task_id, task.title, task.description, task.column_id, task.position)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

## Deletes a task.
@app.delete("/api/tasks/{task_id}", status_code=200)
def delete_task(task_id: int, current_account: Account = Depends(require_write_access)):
    try:
        service.delete_task(task_id)
        return {"message": "Task deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

## Gets a task. Probably don't use this, use Get Board instead.
# @app.get("/api/tasks/{task_id}")
# def get_task(task_id: int):
#     try:
#         return service.get_task(task_id)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))



##### ACCOUNTS #####

## Get all accounts. 
@app.get("/api/accounts")
def get_accounts() -> list[AccountResponse]:
    return [_serialize_account(account) for account in service.get_all_accounts()]

## Get a specific account. 
@app.get("/api/accounts/{account_id}")
def get_account(account_id: int) -> AccountResponse:
    try:
        return _serialize_account(service.get_account(account_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))