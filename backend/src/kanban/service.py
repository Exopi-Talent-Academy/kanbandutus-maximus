from typing import Optional

from .models import Board, Column, Task
from .storage import StorageInterface


class NotFoundError(Exception):
    def __init__(self, entity: str, entity_id: int):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with id={entity_id} not found")


class KanbanService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def get_board(self, board_id: int) -> Board:
        board = self.storage.get_board(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        return board

    def get_all_boards(self) -> list[Board]:
        data = self.storage.load()
        return data.boards

    def create_board(self, name: str) -> Board:
        return self.storage.create_board(name)

    def update_board(self, board_id: int, name: str) -> Board:
        board = self.storage.get_board(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        result = self.storage.update_board(board_id, name)
        if not result:
            raise NotFoundError("Board", board_id)
        return result

    def delete_board(self, board_id: int) -> None:
        board = self.storage.get_board(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        self.storage.delete_board(board_id)

    def get_column(self, column_id: int) -> Column:
        column = self.storage.get_column(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        return column

    def get_columns_by_board(self, board_id: int) -> list[Column]:
        board = self.storage.get_board(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        data = self.storage.load()
        return [c for c in data.columns if c.board_id == board_id]

    def create_column(self, name: str, position: int, board_id: int) -> Column:
        board = self.storage.get_board(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        column = self.storage.create_column(name, position, board_id)
        if not column:
            raise NotFoundError("Board", board_id)
        return column

    def update_column(self, column_id: int, name: str, position: int) -> Column:
        column = self.storage.get_column(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        result = self.storage.update_column(column_id, name, position)
        if not result:
            raise NotFoundError("Column", column_id)
        return result

    def delete_column(self, column_id: int) -> None:
        column = self.storage.get_column(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        self.storage.delete_column(column_id)

    def get_task(self, task_id: int) -> Task:
        task = self.storage.get_task(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        return task

    def get_tasks_by_column(self, column_id: int) -> list[Task]:
        column = self.storage.get_column(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        data = self.storage.load()
        return [t for t in data.tasks if t.column_id == column_id]

    def create_task(self, title: str, description: str, column_id: int, position: int = 0) -> Task:
        column = self.storage.get_column(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        task = self.storage.create_task(title, description, column_id, position)
        if not task:
            raise NotFoundError("Column", column_id)
        return task

    def update_task(self, task_id: int, title: str, description: str, column_id: int, position: int) -> Task:
        task = self.storage.get_task(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        column = self.storage.get_column(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        result = self.storage.update_task(task_id, title, description, column_id, position)
        if not result:
            raise NotFoundError("Task", task_id)
        return result

    def delete_task(self, task_id: int) -> None:
        task = self.storage.get_task(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        self.storage.delete_task(task_id)