import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from .config import get_data_file, get_database_url
from .db import SessionLocal, init_db
from .models import Board, Column, KanbanData, Task
from .orm_models import BoardORM, ColumnORM, TaskORM


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


def _sorted_tasks(tasks: list) -> list:
    return sorted(tasks, key=lambda task: (task.position, task.id))


def _clamp_task_position(position: int, task_count: int) -> int:
    return max(0, min(position, task_count))


def _resequence_tasks(tasks: list) -> None:
    for index, task in enumerate(tasks):
        task.position = index


def _reorder_task(task, source_tasks: list, target_tasks: list, target_column_id: int, target_position: int) -> None:
    source_without_task = [item for item in source_tasks if item.id != task.id]

    if task.column_id == target_column_id:
        insert_at = _clamp_task_position(target_position, len(source_without_task))
        source_without_task.insert(insert_at, task)
        _resequence_tasks(source_without_task)
        return

    target_without_task = [item for item in target_tasks if item.id != task.id]
    insert_at = _clamp_task_position(target_position, len(target_without_task))
    task.column_id = target_column_id
    target_without_task.insert(insert_at, task)
    _resequence_tasks(source_without_task)
    _resequence_tasks(target_without_task)


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
        source_column_id = task.column_id
        source_tasks = _sorted_tasks(data.get_tasks_by_column(source_column_id))
        target_tasks = source_tasks if source_column_id == column_id else _sorted_tasks(data.get_tasks_by_column(column_id))
        task.title = title
        task.description = description
        _reorder_task(task, source_tasks, target_tasks, column_id, position)
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


class SqlAlchemyStorage(StorageInterface):
    def __init__(self):
        should_seed = self._should_seed_from_json()
        init_db()
        if should_seed:
            self._seed_from_default_json()

    def _should_seed_from_json(self) -> bool:
        database_url = get_database_url()
        if not database_url.startswith("sqlite:///"):
            return False

        sqlite_path = database_url.replace("sqlite:///", "", 1)
        return sqlite_path != ":memory:" and not Path(sqlite_path).exists()

    def _seed_from_default_json(self) -> None:
        data_file = get_data_file()
        if not data_file.exists():
            return

        with SessionLocal() as session:
            has_existing_board = session.scalar(select(BoardORM.id).limit(1)) is not None

        if has_existing_board:
            return

        self.save(JsonStorage(data_file).load())

    def _session(self):
        return SessionLocal()

    def _to_domain_board(self, board: BoardORM) -> Board:
        domain_columns: list[Column] = []
        for column in sorted(board.columns, key=lambda c: c.position):
            domain_tasks = [
                Task(
                    id=task.id,
                    title=task.title,
                    column_id=task.column_id,
                    description=task.description,
                    assignee=task.assignee,
                    position=task.position,
                )
                for task in sorted(column.tasks, key=lambda t: t.position)
            ]
            domain_columns.append(
                Column(
                    id=column.id,
                    name=column.name,
                    position=column.position,
                    board_id=column.board_id,
                    tasks=domain_tasks,
                )
            )

        return Board(id=board.id, name=board.name, columns=domain_columns)

    def _to_kanban_data(self, boards: list[BoardORM]) -> KanbanData:
        domain_boards = [self._to_domain_board(board) for board in boards]
        domain_columns = [column for board in domain_boards for column in board.columns]
        domain_tasks = [task for column in domain_columns for task in column.tasks]
        return KanbanData(boards=domain_boards, columns=domain_columns, tasks=domain_tasks)

    def _flatten_columns_tasks(self, data: KanbanData) -> tuple[list[Column], list[Task]]:
        if data.columns:
            columns = data.columns
        else:
            columns = [column for board in data.boards for column in board.columns]

        if data.tasks:
            tasks = data.tasks
        else:
            tasks = [task for column in columns for task in column.tasks]

        return columns, tasks

    def load(self) -> KanbanData:
        with SessionLocal() as session:
            boards = (
                session.execute(
                    select(BoardORM)
                    .options(selectinload(BoardORM.columns).selectinload(ColumnORM.tasks))
                    .order_by(BoardORM.id)
                )
                .scalars()
                .unique()
                .all()
            )
            return self._to_kanban_data(boards)

    def save(self, data: KanbanData) -> None:
        columns, tasks = self._flatten_columns_tasks(data)

        with SessionLocal() as session:
            with session.begin():
                session.execute(delete(TaskORM))
                session.execute(delete(ColumnORM))
                session.execute(delete(BoardORM))

                session.add_all([BoardORM(id=board.id, name=board.name) for board in data.boards])
                session.add_all(
                    [
                        ColumnORM(
                            id=column.id,
                            name=column.name,
                            position=column.position,
                            board_id=column.board_id,
                        )
                        for column in columns
                    ]
                )
                session.add_all(
                    [
                        TaskORM(
                            id=task.id,
                            title=task.title,
                            description=task.description,
                            assignee=task.assignee,
                            position=task.position,
                            column_id=task.column_id,
                        )
                        for task in tasks
                    ]
                )

    def get_board(self, board_id: int) -> Optional[Board]:
        with SessionLocal() as session:
            board = (
                session.execute(
                    select(BoardORM)
                    .where(BoardORM.id == board_id)
                    .options(selectinload(BoardORM.columns).selectinload(ColumnORM.tasks))
                )
                .scalars()
                .unique()
                .first()
            )
            return self._to_domain_board(board) if board else None

    def create_board(self, name: str) -> Board:
        with SessionLocal() as session:
            with session.begin():
                max_id = session.scalar(select(BoardORM.id).order_by(BoardORM.id.desc()).limit(1)) or 0
                board = BoardORM(id=max_id + 1, name=name)
                session.add(board)
            return Board(id=board.id, name=board.name, columns=[])

    def update_board(self, board_id: int, name: str) -> Optional[Board]:
        with SessionLocal() as session:
            with session.begin():
                board = session.get(BoardORM, board_id)
                if not board:
                    return None
                board.name = name

            board = (
                session.execute(
                    select(BoardORM)
                    .where(BoardORM.id == board_id)
                    .options(selectinload(BoardORM.columns).selectinload(ColumnORM.tasks))
                )
                .scalars()
                .unique()
                .first()
            )
            return self._to_domain_board(board) if board else None

    def delete_board(self, board_id: int) -> bool:
        with SessionLocal() as session:
            with session.begin():
                board = session.get(BoardORM, board_id)
                if not board:
                    return False
                session.delete(board)
                return True

    def get_column(self, column_id: int) -> Optional[Column]:
        with SessionLocal() as session:
            column = (
                session.execute(
                    select(ColumnORM).where(ColumnORM.id == column_id).options(selectinload(ColumnORM.tasks))
                )
                .scalars()
                .unique()
                .first()
            )
            if not column:
                return None
            return Column(
                id=column.id,
                name=column.name,
                position=column.position,
                board_id=column.board_id,
                tasks=[
                    Task(
                        id=task.id,
                        title=task.title,
                        column_id=task.column_id,
                        description=task.description,
                        assignee=task.assignee,
                        position=task.position,
                    )
                    for task in sorted(column.tasks, key=lambda t: t.position)
                ],
            )

    def create_column(self, name: str, position: int, board_id: int) -> Optional[Column]:
        with SessionLocal() as session:
            with session.begin():
                board = session.get(BoardORM, board_id)
                if not board:
                    return None
                max_id = session.scalar(select(ColumnORM.id).order_by(ColumnORM.id.desc()).limit(1)) or 0
                column = ColumnORM(id=max_id + 1, name=name, position=position, board_id=board_id)
                session.add(column)
            return Column(id=column.id, name=column.name, position=column.position, board_id=column.board_id, tasks=[])

    def update_column(self, column_id: int, name: str, position: int) -> Optional[Column]:
        with SessionLocal() as session:
            with session.begin():
                column = session.get(ColumnORM, column_id)
                if not column:
                    return None
                column.name = name
                column.position = position
                board_id = column.board_id

            refreshed = (
                session.execute(select(ColumnORM).where(ColumnORM.id == column_id).options(selectinload(ColumnORM.tasks)))
                .scalars()
                .unique()
                .first()
            )
            if not refreshed:
                return None
            return Column(id=refreshed.id, name=refreshed.name, position=refreshed.position, board_id=board_id, tasks=[
                Task(
                    id=task.id,
                    title=task.title,
                    column_id=task.column_id,
                    description=task.description,
                    assignee=task.assignee,
                    position=task.position,
                )
                for task in sorted(refreshed.tasks, key=lambda t: t.position)
            ])

    def delete_column(self, column_id: int) -> bool:
        with SessionLocal() as session:
            with session.begin():
                column = session.get(ColumnORM, column_id)
                if not column:
                    return False
                session.delete(column)
                return True

    def get_task(self, task_id: int) -> Optional[Task]:
        with SessionLocal() as session:
            task = session.get(TaskORM, task_id)
            if not task:
                return None
            return Task(
                id=task.id,
                title=task.title,
                column_id=task.column_id,
                description=task.description,
                assignee=task.assignee,
                position=task.position,
            )

    def create_task(self, title: str, description: str, column_id: int, position: int) -> Optional[Task]:
        with SessionLocal() as session:
            with session.begin():
                column = session.get(ColumnORM, column_id)
                if not column:
                    return None
                max_id = session.scalar(select(TaskORM.id).order_by(TaskORM.id.desc()).limit(1)) or 0
                task = TaskORM(
                    id=max_id + 1,
                    title=title,
                    description=description,
                    assignee="",
                    column_id=column_id,
                    position=position,
                )
                session.add(task)
            return Task(
                id=task.id,
                title=task.title,
                column_id=task.column_id,
                description=task.description,
                assignee=task.assignee,
                position=task.position,
            )

    def update_task(self, task_id: int, title: str, description: str, column_id: int, position: int) -> Optional[Task]:
        with SessionLocal() as session:
            with session.begin():
                task = session.get(TaskORM, task_id)
                if not task:
                    return None
                target_column = session.get(ColumnORM, column_id)
                if not target_column:
                    return None
                source_column_id = task.column_id
                source_tasks = list(
                    session.execute(
                        select(TaskORM)
                        .where(TaskORM.column_id == source_column_id)
                        .order_by(TaskORM.position, TaskORM.id)
                    ).scalars()
                )
                target_tasks = source_tasks if source_column_id == column_id else list(
                    session.execute(
                        select(TaskORM)
                        .where(TaskORM.column_id == column_id)
                        .order_by(TaskORM.position, TaskORM.id)
                    ).scalars()
                )
                task.title = title
                task.description = description
                _reorder_task(task, source_tasks, target_tasks, column_id, position)
            return Task(
                id=task.id,
                title=task.title,
                column_id=task.column_id,
                description=task.description,
                assignee=task.assignee,
                position=task.position,
            )

    def delete_task(self, task_id: int) -> bool:
        with SessionLocal() as session:
            with session.begin():
                task = session.get(TaskORM, task_id)
                if not task:
                    return False
                session.delete(task)
                return True