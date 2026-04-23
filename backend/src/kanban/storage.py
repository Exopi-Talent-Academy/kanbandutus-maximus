"""
Storage implementations for the Kanban application.

This module provides dual storage backends:
- JsonStorage: JSON file-based storage for development
- SqlAlchemyStorage: SQLite database storage using SQLAlchemy ORM

Both implementations support the KanbanStorage interface which aggregates
entity-specific repositories for cleaner dependency injection.
"""

import json
from abc import ABC
from pathlib import Path
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from .config import get_data_file, get_database_url
from .db import SessionLocal, init_db
from .models import Account, Board, Column, KanbanData, Task
from .orm_models import AccountORM, BoardORM, ColumnORM, TaskORM
from .repositories import (
    AccountRepository,
    BoardRepository,
    ColumnRepository,
    KanbanStorage,
    TaskRepository,
)


def _sorted_tasks(tasks: list) -> list:
    """Sort tasks by position, then by ID for stable ordering."""
    return sorted(tasks, key=lambda task: (task.position, task.id))


def _clamp_task_position(position: int, task_count: int) -> int:
    """Clamp a task position to valid range [0, task_count]."""
    return max(0, min(position, task_count))


def _resequence_tasks(tasks: list) -> None:
    """Reassign sequential positions starting from 0."""
    for index, task in enumerate(tasks):
        task.position = index


def _sorted_columns(columns: list) -> list:
    """Sort columns by position, then by ID for stable ordering."""
    return sorted(columns, key=lambda column: (column.position, column.id))


def _clamp_column_position(position: int, column_count: int) -> int:
    """Clamp a column position to valid range [0, column_count]."""
    return max(0, min(position, column_count))


def _resequence_columns(columns: list) -> None:
    """Reassign sequential positions starting from 0."""
    for index, column in enumerate(columns):
        column.position = index


def _reorder_column(column, board_columns: list, target_position: int) -> None:
    """
    Reorder a column within a board by moving it to the target position.

    Args:
        column: The column to reorder
        board_columns: All columns in the board (including the target column)
        target_position: The desired position index
    """
    other_columns = [item for item in board_columns if item.id != column.id]
    insert_at = _clamp_column_position(target_position, len(other_columns))
    other_columns.insert(insert_at, column)
    _resequence_columns(other_columns)


def _reorder_task(
    task,
    source_tasks: list,
    target_tasks: list,
    target_column_id: int,
    target_position: int,
) -> None:
    """
    Reorder a task, potentially moving it to a different column.

    This function handles two scenarios:
    1. Moving within the same column: reorder relative to other tasks
    2. Moving to a different column: remove from source, insert into target

    Args:
        task: The task to reorder
        source_tasks: Tasks in the original column (sorted)
        target_tasks: Tasks in the target column (sorted)
        target_column_id: The destination column ID
        target_position: The desired position in the target column
    """
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


class _BoardRepositoryImpl(BoardRepository):
    """
    Board repository implementation that delegates to the storage class.

    This implementation provides the BoardRepository interface by delegating
    to the underlying storage instance's methods.
    """

    def __init__(self, storage: "JsonStorage | SqlAlchemyStorage"):
        self._storage = storage

    def get(self, board_id: int) -> Optional[Board]:
        """Retrieve a board by ID with nested columns and tasks."""
        return self._storage.get_board(board_id)

    def get_all(self) -> list[Board]:
        """Retrieve all boards with nested structure."""
        data = self._storage.load()
        return data.boards

    def create(self, name: str) -> Board:
        """Create a new board and return it."""
        return self._storage.create_board(name)

    def update(self, board_id: int, name: str) -> Optional[Board]:
        """Update a board's name and return the updated board."""
        return self._storage.update_board(board_id, name)

    def delete(self, board_id: int) -> bool:
        """Delete a board and its cascading data."""
        return self._storage.delete_board(board_id)


class _ColumnRepositoryImpl(ColumnRepository):
    """
    Column repository implementation that delegates to the storage class.

    This implementation provides the ColumnRepository interface by delegating
    to the underlying storage instance's methods.
    """

    def __init__(self, storage: "JsonStorage | SqlAlchemyStorage"):
        self._storage = storage

    def get(self, column_id: int) -> Optional[Column]:
        """Retrieve a column by ID with nested tasks."""
        return self._storage.get_column(column_id)

    def get_by_board(self, board_id: int) -> list[Column]:
        """Retrieve all columns belonging to a board."""
        data = self._storage.load()
        return [c for c in data.columns if c.board_id == board_id]

    def create(self, name: str, position: int, board_id: int) -> Optional[Column]:
        """Create a new column within a board."""
        return self._storage.create_column(name, position, board_id)

    def update(self, column_id: int, name: str, position: int) -> Optional[Column]:
        """Update a column's name and position."""
        return self._storage.update_column(column_id, name, position)

    def delete(self, column_id: int) -> bool:
        """Delete a column and its tasks."""
        return self._storage.delete_column(column_id)


class _TaskRepositoryImpl(TaskRepository):
    """
    Task repository implementation that delegates to the storage class.

    This implementation provides the TaskRepository interface by delegating
    to the underlying storage instance's methods.
    """

    def __init__(self, storage: "JsonStorage | SqlAlchemyStorage"):
        self._storage = storage

    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self._storage.get_task(task_id)

    def get_by_column(self, column_id: int) -> list[Task]:
        """Retrieve all tasks belonging to a column."""
        data = self._storage.load()
        return data.get_tasks_by_column(column_id)

    def create(
        self, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """Create a new task within a column."""
        return self._storage.create_task(title, description, column_id, position)

    def update(
        self, task_id: int, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """Update a task including moving to a different column."""
        return self._storage.update_task(
            task_id, title, description, column_id, position
        )

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID."""
        return self._storage.delete_task(task_id)


class _AccountRepositoryImpl(AccountRepository):
    """
    Account repository implementation that delegates to the storage class.

    This implementation provides the AccountRepository interface by delegating
    to the underlying storage instance's methods.
    """

    def __init__(self, storage: "JsonStorage | SqlAlchemyStorage"):
        self._storage = storage

    def get(self, account_id: int) -> Optional[Account]:
        """Retrieve an account by ID."""
        return self._storage.get_account(account_id)

    def get_all(self) -> list[Account]:
        """Retrieve all accounts."""
        data = self._storage.load()
        return data.accounts


class JsonStorage(KanbanStorage):
    """
    JSON file-based storage implementation for development.

    Reads and writes all data to a single JSON file. Suitable for
    development and testing but not for production use with
    concurrent access.

    Implements the KanbanStorage interface which provides entity-specific
    repository access via properties.
    """

    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._ensure_data_file()
        self._boards_repo: Optional[_BoardRepositoryImpl] = None
        self._columns_repo: Optional[_ColumnRepositoryImpl] = None
        self._tasks_repo: Optional[_TaskRepositoryImpl] = None
        self._accounts_repo: Optional[_AccountRepositoryImpl] = None

    def _ensure_data_file(self) -> None:
        """Verify the data file exists, raising an error if not found."""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

    def _read_file(self) -> dict:
        """Read and parse the JSON data file."""
        with open(self.data_file, "r") as f:
            return json.load(f)

    def _write_file(self, data: dict) -> None:
        """Write data to the JSON data file."""
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def _link_nested_relations(self, data: KanbanData) -> None:
        """Link nested relations between boards, columns, and tasks."""
        columns_by_board: dict[int, list[Column]] = {}
        for column in data.columns:
            columns_by_board.setdefault(column.board_id, []).append(column)

        tasks_by_column: dict[int, list[Task]] = {}
        for task in data.tasks:
            tasks_by_column.setdefault(task.column_id, []).append(task)

        for board in data.boards:
            board_columns = sorted(
                columns_by_board.get(board.id, []), key=lambda c: c.position
            )
            board.columns = board_columns
            for column in board.columns:
                column.tasks = sorted(
                    tasks_by_column.get(column.id, []), key=lambda t: t.position
                )

    def _dict_to_kanban(self, data: dict) -> KanbanData:
        """Convert dictionary data to KanbanData domain model."""
        boards: list[Board] = []
        columns: list[Column] = []
        tasks: list[Task] = []
        accounts: list[Account] = []

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

        if data.get("accounts"):
            accounts = [
                Account(
                    id=account["id"],
                    username=account["username"],
                    password_hash=account.get(
                        "password_hash", account.get("password", "")
                    ),
                    role=account.get("role", "read"),
                )
                for account in data.get("accounts", [])
            ]

        kanban_data = KanbanData(
            boards=boards, columns=columns, tasks=tasks, accounts=accounts
        )
        self._link_nested_relations(kanban_data)
        return kanban_data

    def _kanban_to_dict(self, data: KanbanData) -> dict:
        """Convert KanbanData domain model to dictionary for JSON serialization."""
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
            ],
            "accounts": [
                {
                    "id": account.id,
                    "username": account.username,
                    "password_hash": account.password_hash,
                    "role": account.role,
                }
                for account in data.accounts
            ],
        }

    def load(self) -> KanbanData:
        """Load all data from the JSON file."""
        return self._dict_to_kanban(self._read_file())

    def save(self, data: KanbanData) -> None:
        """Persist all data to the JSON file."""
        self._write_file(self._kanban_to_dict(data))

    def get_board(self, board_id: int) -> Optional[Board]:
        """Get a single board by ID."""
        data = self.load()
        return data.get_board(board_id)

    def get_account(self, account_id: int) -> Optional[Account]:
        """Get a single account by ID."""
        data = self.load()
        for account in data.accounts:
            if account.id == account_id:
                return account
        return None

    def create_board(self, name: str) -> Board:
        """Create a new board and persist to storage."""
        data = self.load()
        new_id = data.get_next_id("board")
        board = Board(id=new_id, name=name, columns=[])
        data.boards.append(board)
        self.save(data)
        return board

    def update_board(self, board_id: int, name: str) -> Optional[Board]:
        """Update a board's name and persist changes."""
        data = self.load()
        board = data.get_board(board_id)
        if board:
            board.name = name
            self.save(data)
        return board

    def delete_board(self, board_id: int) -> bool:
        """Delete a board and all its columns and tasks."""
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
        """Get a single column by ID."""
        data = self.load()
        return data.get_column(column_id)

    def create_column(
        self, name: str, position: int, board_id: int
    ) -> Optional[Column]:
        """Create a new column within a board and persist to storage."""
        data = self.load()
        board = data.get_board(board_id)
        if not board:
            return None
        new_id = data.get_next_id("column")
        column = Column(
            id=new_id, name=name, position=position, board_id=board_id, tasks=[]
        )
        data.columns.append(column)
        board.columns.append(column)
        self.save(data)
        return column

    def update_column(
        self, column_id: int, name: str, position: int
    ) -> Optional[Column]:
        """Update a column's name and position, reordering as needed."""
        data = self.load()
        column = data.get_column(column_id)
        if column:
            board_columns = _sorted_columns(
                [item for item in data.columns if item.board_id == column.board_id]
            )
            column.name = name
            _reorder_column(column, board_columns, position)
            self.save(data)
        return column

    def delete_column(self, column_id: int) -> bool:
        """Delete a column and all its tasks."""
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
        """Get a single task by ID."""
        data = self.load()
        return data.get_task(task_id)

    def create_task(
        self, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """Create a new task within a column and persist to storage."""
        data = self.load()
        column = data.get_column(column_id)
        if not column:
            return None
        new_id = data.get_next_id("task")
        task = Task(
            id=new_id,
            title=title,
            description=description,
            assignee="",
            column_id=column_id,
            position=position,
        )
        data.tasks.append(task)
        column.tasks.append(task)
        self.save(data)
        return task

    def update_task(
        self, task_id: int, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """Update a task's fields and/or move to a different column."""
        data = self.load()
        task = data.get_task(task_id)
        if not task:
            return None
        column = data.get_column(column_id)
        if not column:
            return None
        source_column_id = task.column_id
        source_tasks = _sorted_tasks(data.get_tasks_by_column(source_column_id))
        target_tasks = (
            source_tasks
            if source_column_id == column_id
            else _sorted_tasks(data.get_tasks_by_column(column_id))
        )
        task.title = title
        task.description = description
        _reorder_task(task, source_tasks, target_tasks, column_id, position)
        self.save(data)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        data = self.load()
        task = data.get_task(task_id)
        if not task:
            return False
        data.tasks = [t for t in data.tasks if t.id != task_id]
        self.save(data)
        return True

    @property
    def boards(self) -> BoardRepository:
        """Get the board repository for this storage instance."""
        if self._boards_repo is None:
            self._boards_repo = _BoardRepositoryImpl(self)
        return self._boards_repo

    @property
    def columns(self) -> ColumnRepository:
        """Get the column repository for this storage instance."""
        if self._columns_repo is None:
            self._columns_repo = _ColumnRepositoryImpl(self)
        return self._columns_repo

    @property
    def tasks(self) -> TaskRepository:
        """Get the task repository for this storage instance."""
        if self._tasks_repo is None:
            self._tasks_repo = _TaskRepositoryImpl(self)
        return self._tasks_repo

    @property
    def accounts(self) -> AccountRepository:
        """Get the account repository for this storage instance."""
        if self._accounts_repo is None:
            self._accounts_repo = _AccountRepositoryImpl(self)
        return self._accounts_repo


class SqlAlchemyStorage(KanbanStorage):
    """
    SQLite database storage implementation using SQLAlchemy ORM.

    Provides persistent storage with proper transaction handling.
    Supports automatic database seeding from JSON on first run.

    Implements the KanbanStorage interface which provides entity-specific
    repository access via properties.
    """

    def __init__(self):
        self._boards_repo: Optional[_BoardRepositoryImpl] = None
        self._columns_repo: Optional[_ColumnRepositoryImpl] = None
        self._tasks_repo: Optional[_TaskRepositoryImpl] = None
        self._accounts_repo: Optional[_AccountRepositoryImpl] = None
        should_seed = self._should_seed_from_json()
        init_db()
        if should_seed:
            self._seed_from_default_json()

    def _should_seed_from_json(self) -> bool:
        """Determine if database should be seeded from JSON file."""
        database_url = get_database_url()
        if not database_url.startswith("sqlite:///"):
            return False

        sqlite_path = database_url.replace("sqlite:///", "", 1)
        return sqlite_path != ":memory:" and not Path(sqlite_path).exists()

    def _seed_from_default_json(self) -> None:
        """Seed the database from the default JSON data file if empty."""
        data_file = get_data_file()
        if not data_file.exists():
            return

        with SessionLocal() as session:
            has_existing_data = (
                session.scalar(select(BoardORM.id).limit(1)) is not None
                or session.scalar(select(AccountORM.id).limit(1)) is not None
            )

        if has_existing_data:
            return

        self.save(JsonStorage(data_file).load())

    def _session(self):
        """Create a new database session."""
        return SessionLocal()

    def _to_domain_board(self, board: BoardORM) -> Board:
        """Convert a BoardORM instance to a domain Board model."""
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
        """Convert a list of BoardORM instances to KanbanData."""
        domain_boards = [self._to_domain_board(board) for board in boards]
        domain_columns = [column for board in domain_boards for column in board.columns]
        domain_tasks = [task for column in domain_columns for task in column.tasks]
        return KanbanData(
            boards=domain_boards, columns=domain_columns, tasks=domain_tasks
        )

    def _to_domain_account(self, account: AccountORM) -> Account:
        """Convert an AccountORM instance to a domain Account model."""
        return Account(
            id=account.id,
            username=account.username,
            password_hash=account.password_hash,
            role=account.role,
        )

    def _flatten_columns_tasks(
        self, data: KanbanData
    ) -> tuple[list[Column], list[Task]]:
        """Extract columns and tasks from KanbanData, handling nested structure."""
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
        """Load all data from the database."""
        with SessionLocal() as session:
            boards = (
                session.execute(
                    select(BoardORM)
                    .options(
                        selectinload(BoardORM.columns).selectinload(ColumnORM.tasks)
                    )
                    .order_by(BoardORM.id)
                )
                .scalars()
                .unique()
                .all()
            )
            accounts = (
                session.execute(select(AccountORM).order_by(AccountORM.id))
                .scalars()
                .all()
            )
            data = self._to_kanban_data(list(boards))
            data.accounts = [self._to_domain_account(account) for account in accounts]
            return data

    def save(self, data: KanbanData) -> None:
        """Persist all data to the database using destructive replace pattern."""
        columns, tasks = self._flatten_columns_tasks(data)

        with SessionLocal() as session:
            with session.begin():
                session.execute(delete(AccountORM))
                session.execute(delete(TaskORM))
                session.execute(delete(ColumnORM))
                session.execute(delete(BoardORM))

                session.add_all(
                    [BoardORM(id=board.id, name=board.name) for board in data.boards]
                )
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
                session.add_all(
                    [
                        AccountORM(
                            id=account.id,
                            username=account.username,
                            password_hash=account.password_hash,
                            role=account.role,
                        )
                        for account in data.accounts
                    ]
                )

    def get_board(self, board_id: int) -> Optional[Board]:
        """Get a single board by ID with nested columns and tasks."""
        with SessionLocal() as session:
            board = (
                session.execute(
                    select(BoardORM)
                    .where(BoardORM.id == board_id)
                    .options(
                        selectinload(BoardORM.columns).selectinload(ColumnORM.tasks)
                    )
                )
                .scalars()
                .unique()
                .first()
            )
            return self._to_domain_board(board) if board else None

    def get_account(self, account_id: int) -> Optional[Account]:
        """Get a single account by ID."""
        with SessionLocal() as session:
            account = session.get(AccountORM, account_id)
            return self._to_domain_account(account) if account else None

    def create_board(self, name: str) -> Board:
        """Create a new board and persist to database."""
        with SessionLocal() as session:
            with session.begin():
                max_id = (
                    session.scalar(
                        select(BoardORM.id).order_by(BoardORM.id.desc()).limit(1)
                    )
                    or 0
                )
                board = BoardORM(id=max_id + 1, name=name)
                session.add(board)
            return Board(id=board.id, name=board.name, columns=[])

    def update_board(self, board_id: int, name: str) -> Optional[Board]:
        """Update a board's name and return the updated board."""
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
                    .options(
                        selectinload(BoardORM.columns).selectinload(ColumnORM.tasks)
                    )
                )
                .scalars()
                .unique()
                .first()
            )
            return self._to_domain_board(board) if board else None

    def delete_board(self, board_id: int) -> bool:
        """Delete a board. Cascade deletes are handled by the ORM."""
        with SessionLocal() as session:
            with session.begin():
                board = session.get(BoardORM, board_id)
                if not board:
                    return False
                session.delete(board)
                return True

    def get_column(self, column_id: int) -> Optional[Column]:
        """Get a single column by ID with nested tasks."""
        with SessionLocal() as session:
            column = (
                session.execute(
                    select(ColumnORM)
                    .where(ColumnORM.id == column_id)
                    .options(selectinload(ColumnORM.tasks))
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

    def create_column(
        self, name: str, position: int, board_id: int
    ) -> Optional[Column]:
        """Create a new column within a board and persist to database."""
        with SessionLocal() as session:
            with session.begin():
                board = session.get(BoardORM, board_id)
                if not board:
                    return None
                max_id = (
                    session.scalar(
                        select(ColumnORM.id).order_by(ColumnORM.id.desc()).limit(1)
                    )
                    or 0
                )
                column = ColumnORM(
                    id=max_id + 1, name=name, position=position, board_id=board_id
                )
                session.add(column)
            return Column(
                id=column.id,
                name=column.name,
                position=column.position,
                board_id=column.board_id,
                tasks=[],
            )

    def update_column(
        self, column_id: int, name: str, position: int
    ) -> Optional[Column]:
        """Update a column's name and position, reordering as needed."""
        with SessionLocal() as session:
            with session.begin():
                column = session.get(ColumnORM, column_id)
                if not column:
                    return None
                board_columns = list(
                    session.execute(
                        select(ColumnORM)
                        .where(ColumnORM.board_id == column.board_id)
                        .order_by(ColumnORM.position, ColumnORM.id)
                    ).scalars()
                )
                column.name = name
                board_id = column.board_id
                _reorder_column(column, board_columns, position)

            refreshed = (
                session.execute(
                    select(ColumnORM)
                    .where(ColumnORM.id == column_id)
                    .options(selectinload(ColumnORM.tasks))
                )
                .scalars()
                .unique()
                .first()
            )
            if not refreshed:
                return None
            return Column(
                id=refreshed.id,
                name=refreshed.name,
                position=refreshed.position,
                board_id=board_id,
                tasks=[
                    Task(
                        id=task.id,
                        title=task.title,
                        column_id=task.column_id,
                        description=task.description,
                        assignee=task.assignee,
                        position=task.position,
                    )
                    for task in sorted(refreshed.tasks, key=lambda t: t.position)
                ],
            )

    def delete_column(self, column_id: int) -> bool:
        """Delete a column. Cascade deletes are handled by the ORM."""
        with SessionLocal() as session:
            with session.begin():
                column = session.get(ColumnORM, column_id)
                if not column:
                    return False
                session.delete(column)
                return True

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a single task by ID."""
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

    def create_task(
        self, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """Create a new task within a column and persist to database."""
        with SessionLocal() as session:
            with session.begin():
                column = session.get(ColumnORM, column_id)
                if not column:
                    return None
                max_id = (
                    session.scalar(
                        select(TaskORM.id).order_by(TaskORM.id.desc()).limit(1)
                    )
                    or 0
                )
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

    def update_task(
        self, task_id: int, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """Update a task's fields and/or move to a different column."""
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
                target_tasks = (
                    source_tasks
                    if source_column_id == column_id
                    else list(
                        session.execute(
                            select(TaskORM)
                            .where(TaskORM.column_id == column_id)
                            .order_by(TaskORM.position, TaskORM.id)
                        ).scalars()
                    )
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
        """Delete a task by ID."""
        with SessionLocal() as session:
            with session.begin():
                task = session.get(TaskORM, task_id)
                if not task:
                    return False
                session.delete(task)
                return True

    @property
    def boards(self) -> BoardRepository:
        """Get the board repository for this storage instance."""
        if self._boards_repo is None:
            self._boards_repo = _BoardRepositoryImpl(self)
        return self._boards_repo

    @property
    def columns(self) -> ColumnRepository:
        """Get the column repository for this storage instance."""
        if self._columns_repo is None:
            self._columns_repo = _ColumnRepositoryImpl(self)
        return self._columns_repo

    @property
    def tasks(self) -> TaskRepository:
        """Get the task repository for this storage instance."""
        if self._tasks_repo is None:
            self._tasks_repo = _TaskRepositoryImpl(self)
        return self._tasks_repo

    @property
    def accounts(self) -> AccountRepository:
        """Get the account repository for this storage instance."""
        if self._accounts_repo is None:
            self._accounts_repo = _AccountRepositoryImpl(self)
        return self._accounts_repo


StorageInterface = KanbanStorage
