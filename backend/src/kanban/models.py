from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Board:
    id: int
    name: str
    columns: list["Column"] = field(default_factory=list)


@dataclass
class Column:
    id: int
    name: str
    position: int
    board_id: int
    tasks: list["Task"] = field(default_factory=list)


@dataclass
class Task:
    id: int
    title: str
    column_id: int
    description: str = ""
    assignee: str = ""
    position: int = 0


@dataclass
class KanbanData:
    boards: list[Board] = field(default_factory=list)
    columns: list[Column] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def get_board(self, board_id: int) -> Optional[Board]:
        for board in self.boards:
            if board.id == board_id:
                return board
        return None

    def get_column(self, column_id: int) -> Optional[Column]:
        for column in self.columns:
            if column.id == column_id:
                return column
        return None

    def get_task(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_tasks_by_column(self, column_id: int) -> list[Task]:
        return [t for t in self.tasks if t.column_id == column_id]

    def get_next_id(self, entity_type: str) -> int:
        if entity_type == "board":
            return max((b.id for b in self.boards), default=0) + 1
        elif entity_type == "column":
            return max((c.id for c in self.columns), default=0) + 1
        elif entity_type == "task":
            return max((t.id for t in self.tasks), default=0) + 1
        return 1