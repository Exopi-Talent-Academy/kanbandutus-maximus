"""
Repository interfaces for the Kanban storage layer.

This module defines entity-specific repository interfaces using the
Repository Pattern. Each interface groups related operations for a
single entity type, making it easier to:
- Add new entities (only add one new interface + implementations)
- Test by mocking at the repository level
- Swap implementations without changing consumers

The interfaces follow the Interface Segregation Principle, providing
only the methods needed for each entity rather than a monolithic
storage interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

from .models import Account, Board, Column, KanbanData, Task


class BoardRepository(ABC):
    """
    Repository interface for Board entity operations.

    Provides CRUD operations for boards and loads full board data
    including nested columns and tasks.
    """

    @abstractmethod
    def get(self, board_id: int) -> Optional[Board]:
        """
        Retrieve a board by its ID with all nested columns and tasks.

        Args:
            board_id: The unique identifier of the board

        Returns:
            Board object with nested columns and tasks if found,
            None if board does not exist
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Board]:
        """
        Retrieve all boards with their nested columns and tasks.

        Returns:
            List of all boards with full nested structure
        """
        pass

    @abstractmethod
    def create(self, name: str) -> Board:
        """
        Create a new board with the given name.

        Args:
            name: The name/title for the new board

        Returns:
            The newly created Board object
        """
        pass

    @abstractmethod
    def update(self, board_id: int, name: str) -> Optional[Board]:
        """
        Update an existing board's name.

        Args:
            board_id: The ID of the board to update
            name: The new name for the board

        Returns:
            Updated Board object if found, None if board does not exist
        """
        pass

    @abstractmethod
    def delete(self, board_id: int) -> bool:
        """
        Delete a board and all its cascading data (columns, tasks).

        Args:
            board_id: The ID of the board to delete

        Returns:
            True if board was deleted, False if board did not exist
        """
        pass


class ColumnRepository(ABC):
    """
    Repository interface for Column entity operations.

    Provides CRUD operations for columns and lookups by board.
    """

    @abstractmethod
    def get(self, column_id: int) -> Optional[Column]:
        """
        Retrieve a column by its ID with its nested tasks.

        Args:
            column_id: The unique identifier of the column

        Returns:
            Column object with nested tasks if found,
            None if column does not exist
        """
        pass

    @abstractmethod
    def get_by_board(self, board_id: int) -> list[Column]:
        """
        Retrieve all columns belonging to a specific board.

        Args:
            board_id: The ID of the parent board

        Returns:
            List of columns belonging to the board (without tasks loaded)
        """
        pass

    @abstractmethod
    def create(self, name: str, position: int, board_id: int) -> Optional[Column]:
        """
        Create a new column within a board.

        Args:
            name: The name/title for the column
            position: The position of the column within the board (0-indexed)
            board_id: The ID of the parent board

        Returns:
            Newly created Column object if board exists,
            None if parent board does not exist
        """
        pass

    @abstractmethod
    def update(self, column_id: int, name: str, position: int) -> Optional[Column]:
        """
        Update an existing column's name and/or position.

        Args:
            column_id: The ID of the column to update
            name: The new name for the column
            position: The new position within the board

        Returns:
            Updated Column object with tasks if found,
            None if column does not exist
        """
        pass

    @abstractmethod
    def delete(self, column_id: int) -> bool:
        """
        Delete a column and all its tasks.

        Args:
            column_id: The ID of the column to delete

        Returns:
            True if column was deleted, False if column did not exist
        """
        pass


class TaskRepository(ABC):
    """
    Repository interface for Task entity operations.

    Provides CRUD operations for tasks and lookups by column.
    """

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            Task object if found, None if task does not exist
        """
        pass

    @abstractmethod
    def get_by_column(self, column_id: int) -> list[Task]:
        """
        Retrieve all tasks belonging to a specific column.

        Args:
            column_id: The ID of the parent column

        Returns:
            List of tasks belonging to the column, sorted by position
        """
        pass

    @abstractmethod
    def create(
        self, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """
        Create a new task within a column.

        Args:
            title: The title of the task
            description: Optional description (defaults to empty string)
            column_id: The ID of the parent column
            position: The position within the column (0-indexed)

        Returns:
            Newly created Task object if column exists,
            None if parent column does not exist
        """
        pass

    @abstractmethod
    def update(
        self, task_id: int, title: str, description: str, column_id: int, position: int
    ) -> Optional[Task]:
        """
        Update an existing task's fields including position.

        This method supports moving a task to a different column
        by specifying a new column_id and position.

        Args:
            task_id: The ID of the task to update
            title: The new title for the task
            description: The new description for the task
            column_id: The ID of the target column
            position: The new position within the target column

        Returns:
            Updated Task object if found,
            None if task or target column does not exist
        """
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if task was deleted, False if task did not exist
        """
        pass


class AccountRepository(ABC):
    """
    Repository interface for Account entity operations.

    Provides read-only access to accounts (write operations may be
    added if authentication is implemented).
    """

    @abstractmethod
    def get(self, account_id: int) -> Optional[Account]:
        """
        Retrieve an account by its ID.

        Args:
            account_id: The unique identifier of the account

        Returns:
            Account object if found, None if account does not exist
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Account]:
        """
        Retrieve all accounts.

        Returns:
            List of all accounts
        """
        pass


class KanbanStorage(ABC):
    """
    Storage interface providing data access through repository properties.

    This interface provides only bulk data operations (load/save) and
    entity-specific repository properties. Direct entity CRUD operations
    are not provided; use the repository properties instead.

    Example:
        # Get a board
        board = storage.boards.get(board_id)

        # Get all boards
        boards = storage.boards.get_all()

        # Create a board
        board = storage.boards.create(name="My Board")

        # Update a board
        board = storage.boards.update(board_id, name="New Name")

        # Delete a board
        storage.boards.delete(board_id)

    Note:
        When entities are not found, repository methods return None
        rather than raising exceptions. The service layer is responsible
        for checking results and raising NotFoundError as appropriate.
    """

    @abstractmethod
    def load(self) -> "KanbanData":
        """
        Load all data from storage.

        Returns:
            KanbanData object containing all boards, columns, tasks, and accounts
        """
        pass

    @abstractmethod
    def save(self, data: "KanbanData") -> None:
        """
        Persist all data to storage.

        Args:
            data: The KanbanData object to persist
        """
        pass

    @property
    @abstractmethod
    def boards(self) -> BoardRepository:
        """Get the board repository."""
        pass

    @property
    @abstractmethod
    def columns(self) -> ColumnRepository:
        """Get the column repository."""
        pass

    @property
    @abstractmethod
    def tasks(self) -> TaskRepository:
        """Get the task repository."""
        pass

    @property
    @abstractmethod
    def accounts(self) -> AccountRepository:
        """Get the account repository."""
        pass
