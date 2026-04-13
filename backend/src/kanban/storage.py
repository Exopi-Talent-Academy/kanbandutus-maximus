import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .models import Board, Column, KanbanData, Task


class StorageInterface(ABC):
    @abstractmethod
    def load(self) -> KanbanData:
        pass

    @abstractmethod
    def save(self, data: KanbanData) -> None:
        pass

    @abstractmethod
    def get_board(self, board_id: int) -> Optional[Board]:
        pass

    @abstractmethod
    def create_board(self, name: str) -> Board:
        pass

    @abstractmethod
    def update_board(self, board_id: int, name: str) -> Optional[Board]:
        pass

    @abstractmethod
    def delete_board(self, board_id: int) -> bool:
        pass

    @abstractmethod
    def get_column(self, column_id: int) -> Optional[Column]:
        pass

    @abstractmethod
    def create_column(self, name: str, position: int, board_id: int) -> Optional[Column]:
        pass

    @abstractmethod
    def update_column(self, column_id: int, name: str, position: int) -> Optional[Column]:
        pass

    @abstractmethod
    def delete_column(self, column_id: int) -> bool:
        pass

    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def create_task(self, title: str, description: str, column_id: int, position: int) -> Optional[Task]:
        pass

    @abstractmethod
    def update_task(self, task_id: int, title: str, description: str, column_id: int, position: int) -> Optional[Task]:
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        pass


class JsonStorage(StorageInterface):
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._ensure_data_file()

    def _ensure_data_file(self) -> None:
        if not self.data_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

    def _read_file(self) -> dict:
        with open(self.data_file, "r") as f:
            return json.load(f)

    def _write_file(self, data: dict) -> None:
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def _dict_to_kanban(self, data: dict) -> KanbanData:
        boards = [Board(id=b["id"], name=b["name"], columns=b.get("columns", [])) for b in data.get("boards", [])]
        columns = [Column(id=c["id"], name=c["name"], position=c["position"], board_id=c.get("board_id", 0)) for c in data.get("columns", [])]
        tasks = [Task(id=t["id"], title=t["title"], description=t.get("description", ""), column_id=t.get("column_id", 0), position=t.get("position", 0)) for t in data.get("tasks", [])]
        return KanbanData(boards=boards, columns=columns, tasks=tasks)

    def _kanban_to_dict(self, data: KanbanData) -> dict:
        return {
            "boards": [{"id": b.id, "name": b.name, "columns": b.columns} for b in data.boards],
            "columns": [{"id": c.id, "name": c.name, "position": c.position, "board_id": c.board_id} for c in data.columns],
            "tasks": [{"id": t.id, "title": t.title, "description": t.description, "column_id": t.column_id, "position": t.position} for t in data.tasks]
        }

    def load(self) -> KanbanData:
        return self._dict_to_kanban(self._read_file())

    def save(self, data: KanbanData) -> None:
        self._write_file(self._kanban_to_dict(data))

    def get_board(self, board_id: int) -> Optional[Board]:
        data = self.load()
        return data.get_board(board_id)

    def create_board(self, name: str) -> Board:
        data = self.load()
        new_id = data.get_next_id("board")
        board = Board(id=new_id, name=name, columns=[])
        data.boards.append(board)
        self.save(data)
        return board

    def update_board(self, board_id: int, name: str) -> Optional[Board]:
        data = self.load()
        board = data.get_board(board_id)
        if board:
            board.name = name
            self.save(data)
        return board

    def delete_board(self, board_id: int) -> bool:
        data = self.load()
        board = data.get_board(board_id)
        if not board:
            return False
        columns_to_delete = [c.id for c in data.columns if c.board_id == board_id]
        data.tasks = [t for t in data.tasks if t.column_id not in columns_to_delete]
        data.columns = [c for c in data.columns if c.board_id != board_id]
        data.boards = [b for b in data.boards if b.id != board_id]
        self.save(data)
        return True

    def get_column(self, column_id: int) -> Optional[Column]:
        data = self.load()
        return data.get_column(column_id)

    def create_column(self, name: str, position: int, board_id: int) -> Optional[Column]:
        data = self.load()
        board = data.get_board(board_id)
        if not board:
            return None
        new_id = data.get_next_id("column")
        column = Column(id=new_id, name=name, position=position, board_id=board_id)
        data.columns.append(column)
        board.columns.append(new_id)
        self.save(data)
        return column

    def update_column(self, column_id: int, name: str, position: int) -> Optional[Column]:
        data = self.load()
        column = data.get_column(column_id)
        if column:
            column.name = name
            column.position = position
            self.save(data)
        return column

    def delete_column(self, column_id: int) -> bool:
        data = self.load()
        column = data.get_column(column_id)
        if not column:
            return False
        data.tasks = [t for t in data.tasks if t.column_id != column_id]
        data.columns = [c for c in data.columns if c.id != column_id]
        for board in data.boards:
            if column_id in board.columns:
                board.columns.remove(column_id)
        self.save(data)
        return True

    def get_task(self, task_id: int) -> Optional[Task]:
        data = self.load()
        return data.get_task(task_id)

    def create_task(self, title: str, description: str, column_id: int, position: int) -> Optional[Task]:
        data = self.load()
        column = data.get_column(column_id)
        if not column:
            return None
        new_id = data.get_next_id("task")
        task = Task(id=new_id, title=title, description=description, column_id=column_id, position=position)
        data.tasks.append(task)
        self.save(data)
        return task

    def update_task(self, task_id: int, title: str, description: str, column_id: int, position: int) -> Optional[Task]:
        data = self.load()
        task = data.get_task(task_id)
        if not task:
            return None
        column = data.get_column(column_id)
        if not column:
            return None
        task.title = title
        task.description = description
        task.column_id = column_id
        task.position = position
        self.save(data)
        return task

    def delete_task(self, task_id: int) -> bool:
        data = self.load()
        task = data.get_task(task_id)
        if not task:
            return False
        data.tasks = [t for t in data.tasks if t.id != task_id]
        self.save(data)
        return True