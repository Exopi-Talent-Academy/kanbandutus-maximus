from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import get_data_file
from .frontend import AngularMock, FrontendInterface
from .service import KanbanService, NotFoundError
from .storage import JsonStorage, StorageInterface

app = FastAPI(title="Kanban API")


def get_storage() -> StorageInterface:
    return JsonStorage(get_data_file())


def get_frontend() -> FrontendInterface:
    return AngularMock()


service = KanbanService(get_storage())


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


@app.get("/api/boards")
def get_boards():
    return service.get_all_boards()


@app.get("/api/boards/{board_id}")
def get_board(board_id: int):
    try:
        return service.get_board(board_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/boards")
def create_board(board: BoardCreate):
    return service.create_board(board.name)


@app.put("/api/boards/{board_id}")
def update_board(board_id: int, board: BoardUpdate):
    try:
        return service.update_board(board_id, board.name)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/boards/{board_id}")
def delete_board(board_id: int):
    try:
        service.delete_board(board_id)
        return {"message": "Board deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/boards/{board_id}/columns")
def get_columns(board_id: int):
    try:
        return service.get_columns_by_board(board_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/columns")
def create_column(column: ColumnCreate):
    try:
        return service.create_column(column.name, column.position, column.board_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/api/columns/{column_id}")
def update_column(column_id: int, column: ColumnUpdate):
    try:
        return service.update_column(column_id, column.name, column.position)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/columns/{column_id}")
def delete_column(column_id: int):
    try:
        service.delete_column(column_id)
        return {"message": "Column deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/columns/{column_id}/tasks")
def get_tasks(column_id: int):
    try:
        return service.get_tasks_by_column(column_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/tasks")
def create_task(task: TaskCreate):
    try:
        return service.create_task(task.title, task.description, task.column_id, task.position)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    try:
        return service.update_task(task_id, task.title, task.description, task.column_id, task.position)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        service.delete_task(task_id)
        return {"message": "Task deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/tasks/{task_id}")
def get_task(task_id: int):
    try:
        return service.get_task(task_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))