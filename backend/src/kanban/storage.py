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

    def _link_nested_relations(self, data: KanbanData) -> None:
        columns_by_board: dict[int, list[Column]] = {}
        for column in data.columns:
            columns_by_board.setdefault(column.board_id, []).append(column)

        tasks_by_column: dict[int, list[Task]] = {}
        for task in data.tasks:
            tasks_by_column.setdefault(task.column_id, []).append(task)

        for board in data.boards:
            board_columns = sorted(columns_by_board.get(board.id, []), key=lambda c: c.position)
            board.columns = board_columns
            for column in board.columns:
                column.tasks = sorted(tasks_by_column.get(column.id, []), key=lambda t: t.position)

    def _dict_to_kanban(self, data: dict) -> KanbanData:
        boards: list[Board] = []
        columns: list[Column] = []
        tasks: list[Task] = []

        # Backward-compatible read: supports nested board->columns->tasks and flat arrays.
        for board_data in data.get("boards", []):
            board = Board(id=board_data["id"], name=board_data["name"], columns=[])
            boards.append(board)

            for column_data in board_data.get("columns", []):
                column = Column(
                    id=column_data["id"],
                    name=column_data["name"],
                    position=column_data["position"],
                    board_id=column_data.get("board_id", board.id),
                    tasks=[],
                )
                columns.append(column)

                for task_data in column_data.get("tasks", []):
                    tasks.append(
                        Task(
                            id=task_data["id"],
                            title=task_data["title"],
                            description=task_data.get("description", ""),
                            assignee=task_data.get("assignee", ""),
                            column_id=task_data.get("column_id", column.id),
                            position=task_data.get("position", 0),
                        )
                    )

        if data.get("columns"):
            columns = [
                Column(
                    id=c["id"],
                    name=c["name"],
                    position=c["position"],
                    board_id=c.get("board_id", 0),
                    tasks=[],
                )
                for c in data.get("columns", [])
            ]

        if data.get("tasks"):
            tasks = [
                Task(
                    id=t["id"],
                    title=t["title"],
                    description=t.get("description", ""),
                    assignee=t.get("assignee", ""),
                    column_id=t.get("column_id", 0),
                    position=t.get("position", 0),
                )
                for t in data.get("tasks", [])
            ]

        kanban_data = KanbanData(boards=boards, columns=columns, tasks=tasks)
        self._link_nested_relations(kanban_data)
        return kanban_data

    def _kanban_to_dict(self, data: KanbanData) -> dict:
        self._link_nested_relations(data)
        return {
            "boards": [
                {
                    "id": board.id,
                    "name": board.name,
                    "columns": [
                        {
                            "id": column.id,
                            "name": column.name,
                            "position": column.position,
                            "board_id": column.board_id,
                            "tasks": [
                                {
                                    "id": task.id,
                                    "title": task.title,
                                    "description": task.description,
                                    "assignee": task.assignee,
                                    "column_id": task.column_id,
                                    "position": task.position,
                                }
                                for task in column.tasks
                            ],
                        }
                        for column in board.columns
                    ],
                }
                for board in data.boards
            ]
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
        column = Column(id=new_id, name=name, position=position, board_id=board_id, tasks=[])
        data.columns.append(column)
        board.columns.append(column)
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
            board.columns = [c for c in board.columns if c.id != column_id]
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
        task = Task(id=new_id, title=title, description=description, assignee="", column_id=column_id, position=position)
        data.tasks.append(task)
        column.tasks.append(task)
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