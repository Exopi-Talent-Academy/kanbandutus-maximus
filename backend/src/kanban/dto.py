"""
Data Transfer Objects (DTOs) for the Kanban API.

This module defines request and response models used for API communication.
DTOs serve two purposes:
1. Validate incoming request data with Pydantic
2. Decouple domain models from the external API contract

Using DTOs allows the domain model to evolve independently of the API,
and ensures consistent validation at the API boundary.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import Account, Board, Column, Task


class ColumnCreate(BaseModel):
    """
    Request DTO for creating a new column.

    Expects:
        - name: Non-empty string, 1-50 characters
        - position: Non-negative integer representing column order
        - board_id: ID of the parent board this column belongs to
    """

    name: str = Field(
        min_length=1, max_length=50, description="The name/title of the column"
    )
    position: int = Field(
        ge=0, description="The position of the column within the board (0-indexed)"
    )
    board_id: int = Field(
        gt=0, description="The ID of the board this column belongs to"
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        """Strip whitespace and reject purely whitespace names."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Column name cannot be empty or whitespace only")
        return stripped


class ColumnUpdate(BaseModel):
    """
    Request DTO for updating an existing column.

    Expects:
        - name: Non-empty string, 1-50 characters
        - position: Non-negative integer for column repositioning
    """

    name: str = Field(
        min_length=1, max_length=50, description="The updated name/title of the column"
    )
    position: int = Field(
        ge=0, description="The new position of the column within the board"
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        """Strip whitespace and reject purely whitespace names."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Column name cannot be empty or whitespace only")
        return stripped


class TaskCreate(BaseModel):
    """
    Request DTO for creating a new task.

    Expects:
        - title: Non-empty string, 1-50 characters
        - description: Optional string, max 200 characters
        - column_id: ID of the parent column
        - position: Non-negative integer for task ordering
    """

    title: str = Field(min_length=1, max_length=50, description="The title of the task")
    description: str = Field(
        default="", max_length=200, description="Optional description of the task"
    )
    column_id: int = Field(
        gt=0, description="The ID of the column this task belongs to"
    )
    position: int = Field(
        default=0,
        ge=0,
        description="The position of the task within the column (0-indexed)",
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        """Strip whitespace and reject purely whitespace titles."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty or whitespace only")
        return stripped


class TaskUpdate(BaseModel):
    """
    Request DTO for updating an existing task.

    Expects:
        - title: Non-empty string, 1-50 characters
        - description: String, max 200 characters
        - column_id: ID of the target column (for moving tasks)
        - position: Non-negative integer for task repositioning
    """

    title: str = Field(
        min_length=1, max_length=50, description="The updated title of the task"
    )
    description: str = Field(
        default="", max_length=200, description="The updated description of the task"
    )
    column_id: int = Field(gt=0, description="The ID of the target column")
    position: int = Field(
        ge=0, description="The new position of the task within the target column"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        """Strip whitespace and reject purely whitespace titles."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty or whitespace only")
        return stripped


class TaskResponse(BaseModel):
    """
    Response DTO for a single task.

    Exposes only the fields relevant to API consumers, without leaking
    internal domain model details.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Unique identifier for the task")
    title: str = Field(description="The title of the task")
    description: str = Field(description="The task description")
    assignee: str = Field(description="The username of the task assignee")
    position: int = Field(description="The position of the task within its column")
    column_id: int = Field(description="The ID of the column containing this task")


class ColumnResponse(BaseModel):
    """
    Response DTO for a single column.

    Includes the column's tasks to support nested data representation.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Unique identifier for the column")
    name: str = Field(description="The name of the column")
    position: int = Field(description="The position of the column within its board")
    board_id: int = Field(description="The ID of the board containing this column")
    tasks: list[TaskResponse] = Field(
        default_factory=list, description="List of tasks within this column"
    )


class BoardResponse(BaseModel):
    """
    Response DTO for a single board.

    Includes all columns with their nested tasks for complete board representation.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Unique identifier for the board")
    name: str = Field(description="The name of the board")
    columns: list[ColumnResponse] = Field(
        default_factory=list, description="List of columns within this board"
    )


class AccountResponse(BaseModel):
    """
    Response DTO for an account.

    Note: Excludes sensitive fields like password_hash to prevent
    accidental exposure in API responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Unique identifier for the account")
    username: str = Field(description="The username")
    role: str = Field(description="The role of the account (read, write, admin)")


def task_to_dto(task: Task) -> TaskResponse:
    """
    Convert a domain Task model to a TaskResponse DTO.

    Args:
        task: The domain Task model to convert

    Returns:
        TaskResponse DTO populated with the task's data
    """
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        assignee=task.assignee,
        position=task.position,
        column_id=task.column_id,
    )


def column_to_dto(column: Column, include_tasks: bool = True) -> ColumnResponse:
    """
    Convert a domain Column model to a ColumnResponse DTO.

    Args:
        column: The domain Column model to convert
        include_tasks: Whether to include nested tasks in the response

    Returns:
        ColumnResponse DTO populated with the column's data
    """
    tasks = []
    if include_tasks:
        tasks = [task_to_dto(task) for task in column.tasks]

    return ColumnResponse(
        id=column.id,
        name=column.name,
        position=column.position,
        board_id=column.board_id,
        tasks=tasks,
    )


def board_to_dto(board: Board) -> BoardResponse:
    """
    Convert a domain Board model to a BoardResponse DTO.

    Args:
        board: The domain Board model to convert

    Returns:
        BoardResponse DTO populated with the board's data including all columns and tasks
    """
    columns = [column_to_dto(column, include_tasks=True) for column in board.columns]

    return BoardResponse(
        id=board.id,
        name=board.name,
        columns=columns,
    )


def account_to_dto(account: Account) -> AccountResponse:
    """
    Convert a domain Account model to an AccountResponse DTO.

    Args:
        account: The domain Account model to convert

    Returns:
        AccountResponse DTO populated with the account's data (excluding password)
    """
    return AccountResponse(
        id=account.id,
        username=account.username,
        role=account.role,
    )
