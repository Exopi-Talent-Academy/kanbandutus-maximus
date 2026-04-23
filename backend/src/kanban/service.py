"""
Service layer for the Kanban application.

This module implements the business logic layer, sitting between the API
presentation layer and the storage/data access layer. Its responsibilities:

1. Business Rule Enforcement
   - Cascade delete: Board deletion cascades to columns and tasks
   - Positional reordering: Tasks and columns maintain consistent ordering
   - Entity validation: Ensure referenced entities exist before operations

2. Domain-DTO Mapping
   - Converts domain models to DTOs for API responses
   - Isolates API consumers from domain model changes

3. Error Handling
   - Raises NotFoundError for missing entities
   - Errors are caught and formatted by the API layer

The service layer should not contain:
- HTTP-related code (belongs in main.py)
- Data persistence logic (belongs in storage.py)
- Database-specific details (belongs in orm_models.py)
"""

from .dto import (
    AccountResponse,
    account_to_dto,
    board_to_dto,
    column_to_dto,
    task_to_dto,
)
from .models import Account, Board, Column, Task
from .repositories import KanbanStorage


class NotFoundError(Exception):
    """
    Exception raised when an entity is not found.

    Attributes:
        entity: The type of entity that was not found (e.g., "Board", "Column")
        entity_id: The ID of the entity that was not found
    """

    def __init__(self, entity: str, entity_id: int):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with id={entity_id} not found")


class KanbanService:
    """
    Service layer facade for Kanban board operations.

    Provides business logic and domain-DTO mapping for all kanban operations.
    Consumers should use this service rather than calling storage directly
    to ensure business rules are consistently applied.

    Attributes:
        storage: The underlying storage interface for data persistence
    """

    def __init__(self, storage: KanbanStorage):
        """
        Initialize the service with a storage backend.

        Args:
            storage: A storage implementation (JsonStorage or SqlAlchemyStorage)
        """
        self.storage = storage

    def get_board(self, board_id: int) -> Board:
        """
        Get a board by ID.

        Args:
            board_id: The unique identifier of the board

        Returns:
            The Board domain model with nested columns and tasks

        Raises:
            NotFoundError: If the board does not exist
        """
        board = self.storage.boards.get(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        return board

    def get_board_dto(self, board_id: int) -> dict:
        """
        Get a board as a DTO for API response.

        Args:
            board_id: The unique identifier of the board

        Returns:
            Dictionary representation of the board for JSON serialization

        Raises:
            NotFoundError: If the board does not exist
        """
        board = self.get_board(board_id)
        return board_to_dto(board).model_dump()

    def get_all_boards(self) -> list[Board]:
        """
        Get all boards.

        Returns:
            List of all Board domain models
        """
        return self.storage.boards.get_all()

    def get_all_boards_dto(self) -> list[dict]:
        """
        Get all boards as DTOs for API response.

        Returns:
            List of board dictionaries for JSON serialization
        """
        boards = self.get_all_boards()
        return [board_to_dto(board).model_dump() for board in boards]

    def create_board(self, name: str) -> Board:
        """
        Create a new board.

        Args:
            name: The name/title for the new board

        Returns:
            The newly created Board domain model
        """
        return self.storage.boards.create(name)

    def create_board_dto(self, name: str) -> dict:
        """
        Create a new board and return as DTO.

        Args:
            name: The name/title for the new board

        Returns:
            Dictionary representation of the created board
        """
        board = self.create_board(name)
        return board_to_dto(board).model_dump()

    def update_board(self, board_id: int, name: str) -> Board:
        """
        Update a board's name.

        Args:
            board_id: The ID of the board to update
            name: The new name for the board

        Returns:
            The updated Board domain model

        Raises:
            NotFoundError: If the board does not exist
        """
        board = self.storage.boards.get(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        result = self.storage.boards.update(board_id, name)
        if not result:
            raise NotFoundError("Board", board_id)
        return result

    def delete_board(self, board_id: int) -> None:
        """
        Delete a board and all its cascading data.

        Business Rule: Deleting a board must also delete:
        1. All columns belonging to the board
        2. All tasks belonging to those columns

        This cascade is handled by the storage layer's delete_board method,
        but is documented here as a business requirement.

        Args:
            board_id: The ID of the board to delete

        Raises:
            NotFoundError: If the board does not exist
        """
        board = self.storage.boards.get(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        self.storage.boards.delete(board_id)

    def get_column(self, column_id: int) -> Column:
        """
        Get a column by ID.

        Args:
            column_id: The unique identifier of the column

        Returns:
            The Column domain model with nested tasks

        Raises:
            NotFoundError: If the column does not exist
        """
        column = self.storage.columns.get(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        return column

    def get_column_dto(self, column_id: int) -> dict:
        """
        Get a column as a DTO for API response.

        Args:
            column_id: The unique identifier of the column

        Returns:
            Dictionary representation of the column for JSON serialization

        Raises:
            NotFoundError: If the column does not exist
        """
        column = self.get_column(column_id)
        return column_to_dto(column).model_dump()

    def get_columns_by_board(self, board_id: int) -> list[Column]:
        """
        Get all columns belonging to a board.

        Args:
            board_id: The ID of the parent board

        Returns:
            List of Column domain models belonging to the board

        Raises:
            NotFoundError: If the board does not exist
        """
        board = self.storage.boards.get(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        return self.storage.columns.get_by_board(board_id)

    def create_column(self, name: str, position: int, board_id: int) -> Column:
        """
        Create a new column within a board.

        Args:
            name: The name/title for the column
            position: The position of the column within the board (0-indexed)
            board_id: The ID of the parent board

        Returns:
            The newly created Column domain model

        Raises:
            NotFoundError: If the parent board does not exist
        """
        board = self.storage.boards.get(board_id)
        if not board:
            raise NotFoundError("Board", board_id)
        column = self.storage.columns.create(name, position, board_id)
        if not column:
            raise NotFoundError("Board", board_id)
        return column

    def create_column_dto(self, name: str, position: int, board_id: int) -> dict:
        """
        Create a new column and return as DTO.

        Args:
            name: The name/title for the column
            position: The position of the column within the board
            board_id: The ID of the parent board

        Returns:
            Dictionary representation of the created column

        Raises:
            NotFoundError: If the parent board does not exist
        """
        column = self.create_column(name, position, board_id)
        return column_to_dto(column).model_dump()

    def update_column(self, column_id: int, name: str, position: int) -> Column:
        """
        Update a column's name and/or position.

        Business Rule: When updating position, the column is moved to that
        position and other columns are reordered accordingly.

        Args:
            column_id: The ID of the column to update
            name: The new name for the column
            position: The new position within the board

        Returns:
            The updated Column domain model

        Raises:
            NotFoundError: If the column does not exist
        """
        column = self.storage.columns.get(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        result = self.storage.columns.update(column_id, name, position)
        if not result:
            raise NotFoundError("Column", column_id)
        return result

    def update_column_dto(self, column_id: int, name: str, position: int) -> dict:
        """
        Update a column and return as DTO.

        Args:
            column_id: The ID of the column to update
            name: The new name for the column
            position: The new position within the board

        Returns:
            Dictionary representation of the updated column

        Raises:
            NotFoundError: If the column does not exist
        """
        column = self.update_column(column_id, name, position)
        return column_to_dto(column).model_dump()

    def delete_column(self, column_id: int) -> None:
        """
        Delete a column and all its tasks.

        Business Rule: Deleting a column must also delete all tasks
        belonging to that column. This is enforced by the storage layer.

        Args:
            column_id: The ID of the column to delete

        Raises:
            NotFoundError: If the column does not exist
        """
        column = self.storage.columns.get(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        self.storage.columns.delete(column_id)

    def get_task(self, task_id: int) -> Task:
        """
        Get a task by ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The Task domain model

        Raises:
            NotFoundError: If the task does not exist
        """
        task = self.storage.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        return task

    def get_task_dto(self, task_id: int) -> dict:
        """
        Get a task as a DTO for API response.

        Args:
            task_id: The unique identifier of the task

        Returns:
            Dictionary representation of the task for JSON serialization

        Raises:
            NotFoundError: If the task does not exist
        """
        task = self.get_task(task_id)
        return task_to_dto(task).model_dump()

    def get_tasks_by_column(self, column_id: int) -> list[Task]:
        """
        Get all tasks belonging to a column.

        Args:
            column_id: The ID of the parent column

        Returns:
            List of Task domain models belonging to the column

        Raises:
            NotFoundError: If the column does not exist
        """
        column = self.storage.columns.get(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        return self.storage.tasks.get_by_column(column_id)

    def get_tasks_by_column_dto(self, column_id: int) -> list[dict]:
        """
        Get all tasks belonging to a column as DTOs.

        Args:
            column_id: The ID of the parent column

        Returns:
            List of task dictionaries for JSON serialization

        Raises:
            NotFoundError: If the column does not exist
        """
        tasks = self.get_tasks_by_column(column_id)
        return [task_to_dto(task).model_dump() for task in tasks]

    def create_task(
        self, title: str, description: str, column_id: int, position: int = 0
    ) -> Task:
        """
        Create a new task within a column.

        Args:
            title: The title of the task
            description: Optional description (defaults to empty string)
            column_id: The ID of the parent column
            position: The position within the column (0-indexed, defaults to 0)

        Returns:
            The newly created Task domain model

        Raises:
            NotFoundError: If the parent column does not exist
        """
        column = self.storage.columns.get(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        task = self.storage.tasks.create(title, description, column_id, position)
        if not task:
            raise NotFoundError("Column", column_id)
        return task

    def create_task_dto(
        self, title: str, description: str, column_id: int, position: int = 0
    ) -> dict:
        """
        Create a new task and return as DTO.

        Args:
            title: The title of the task
            description: Optional description
            column_id: The ID of the parent column
            position: The position within the column

        Returns:
            Dictionary representation of the created task

        Raises:
            NotFoundError: If the parent column does not exist
        """
        task = self.create_task(title, description, column_id, position)
        return task_to_dto(task).model_dump()

    def update_task(
        self, task_id: int, title: str, description: str, column_id: int, position: int
    ) -> Task:
        """
        Update a task's fields and/or move to a different column.

        Business Rule: When updating position and/or column_id, the task
        is repositioned accordingly:
        - Tasks in the source column are reordered
        - Tasks in the target column are reordered (if different column)
        - The task's column_id is updated if moved

        Args:
            task_id: The ID of the task to update
            title: The new title for the task
            description: The new description for the task
            column_id: The ID of the target column
            position: The new position within the target column

        Returns:
            The updated Task domain model

        Raises:
            NotFoundError: If the task or target column does not exist
        """
        task = self.storage.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        column = self.storage.columns.get(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        result = self.storage.tasks.update(
            task_id, title, description, column_id, position
        )
        if not result:
            raise NotFoundError("Task", task_id)
        return result

    def update_task_dto(
        self, task_id: int, title: str, description: str, column_id: int, position: int
    ) -> dict:
        """
        Update a task and return as DTO.

        Args:
            task_id: The ID of the task to update
            title: The new title for the task
            description: The new description for the task
            column_id: The ID of the target column
            position: The new position within the target column

        Returns:
            Dictionary representation of the updated task

        Raises:
            NotFoundError: If the task or target column does not exist
        """
        task = self.update_task(task_id, title, description, column_id, position)
        return task_to_dto(task).model_dump()

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task by ID.

        Args:
            task_id: The ID of the task to delete

        Raises:
            NotFoundError: If the task does not exist
        """
        task = self.storage.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        self.storage.tasks.delete(task_id)

    def move_task(self, task_id: int, target_column_id: int, position: int) -> Task:
        """
        Move a task to a different column and/or position.

        Business Rule: This is a specialized operation for moving tasks
        that may be exposed as a dedicated API endpoint in the future.
        Currently delegates to update_task.

        Args:
            task_id: The ID of the task to move
            target_column_id: The ID of the destination column
            position: The desired position within the destination column

        Returns:
            The moved Task domain model

        Raises:
            NotFoundError: If the task or target column does not exist
        """
        task = self.storage.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        target_column = self.storage.columns.get(target_column_id)
        if not target_column:
            raise NotFoundError("Column", target_column_id)
        result = self.storage.tasks.update(
            task_id, task.title, task.description, target_column_id, position
        )
        if not result:
            raise NotFoundError("Task", task_id)
        return result

    def move_column(self, column_id: int, position: int) -> Column:
        """
        Move a column to a different position within its board.

        Business Rule: This is a specialized operation for moving columns
        that may be exposed as a dedicated API endpoint in the future.
        Currently delegates to update_column.

        Args:
            column_id: The ID of the column to move
            position: The desired position within the board

        Returns:
            The moved Column domain model

        Raises:
            NotFoundError: If the column does not exist
        """
        column = self.storage.columns.get(column_id)
        if not column:
            raise NotFoundError("Column", column_id)
        result = self.storage.columns.update(column_id, column.name, position)
        if not result:
            raise NotFoundError("Column", column_id)
        return result

    def get_account(self, account_id: int) -> Account:
        """
        Get an account by ID.

        Args:
            account_id: The unique identifier of the account

        Returns:
            The Account domain model

        Raises:
            NotFoundError: If the account does not exist
        """
        account = self.storage.accounts.get(account_id)
        if not account:
            raise NotFoundError("Account", account_id)
        return account

    def get_account_dto(self, account_id: int) -> AccountResponse:
        """
        Get an account as a DTO for API response.

        Args:
            account_id: The unique identifier of the account

        Returns:
            AccountResponse DTO (excludes password_hash)

        Raises:
            NotFoundError: If the account does not exist
        """
        account = self.get_account(account_id)
        return account_to_dto(account)

    def get_all_accounts(self) -> list[Account]:
        """
        Get all accounts.

        Returns:
            List of all Account domain models
        """
        return self.storage.accounts.get_all()

    def get_all_accounts_dto(self) -> list[AccountResponse]:
        """
        Get all accounts as DTOs for API response.

        Returns:
            List of AccountResponse DTOs (excludes password_hash)
        """
        accounts = self.get_all_accounts()
        return [account_to_dto(account) for account in accounts]
