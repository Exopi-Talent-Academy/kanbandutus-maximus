import json
import tempfile
from pathlib import Path

import pytest

from src.kanban.models import Board, Column, Task
from src.kanban.storage import JsonStorage, StorageInterface


@pytest.fixture
def temp_data_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        data = {
            "boards": [{"id": 1, "name": "Test Board", "columns": [1, 2]}],
            "columns": [
                {"id": 1, "name": "To Do", "position": 0, "board_id": 1},
                {"id": 2, "name": "Done", "position": 1, "board_id": 1}
            ],
            "tasks": [{"id": 1, "title": "Test Task", "description": "Test", "column_id": 1, "position": 0}]
        }
        json.dump(data, f)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


@pytest.fixture
def storage(temp_data_file) -> JsonStorage:
    return JsonStorage(temp_data_file)


def test_get_board(storage):
    board = storage.get_board(1)
    assert board is not None
    assert board.name == "Test Board"
    assert 1 in board.columns


def test_get_board_not_found(storage):
    board = storage.get_board(999)
    assert board is None


def test_get_column(storage):
    column = storage.get_column(1)
    assert column is not None
    assert column.name == "To Do"
    assert column.position == 0


def test_get_task(storage):
    task = storage.get_task(1)
    assert task is not None
    assert task.title == "Test Task"


def test_create_board(storage):
    board = storage.create_board("New Board")
    assert board.id == 2
    assert board.name == "New Board"


def test_create_column(storage):
    column = storage.create_column("In Progress", 2, 1)
    assert column is not None
    assert column.name == "In Progress"
    assert column.position == 2


def test_create_column_invalid_board(storage):
    column = storage.create_column("Fail", 0, 999)
    assert column is None


def test_create_task(storage):
    task = storage.create_task("New Task", "Description", 1, 1)
    assert task is not None
    assert task.title == "New Task"


def test_create_task_invalid_column(storage):
    task = storage.create_task("Fail", "", 999, 0)
    assert task is None


def test_delete_board(storage):
    result = storage.delete_board(1)
    assert result is True
    assert storage.get_board(1) is None


def test_delete_column(storage):
    result = storage.delete_column(1)
    assert result is True
    assert storage.get_column(1) is None


def test_delete_task(storage):
    result = storage.delete_task(1)
    assert result is True
    assert storage.get_task(1) is None


def test_update_board(storage):
    board = storage.update_board(1, "Updated Board")
    assert board is not None
    assert board.name == "Updated Board"


def test_update_column(storage):
    column = storage.update_column(1, "Updated Column", 5)
    assert column is not None
    assert column.name == "Updated Column"
    assert column.position == 5


def test_update_task(storage):
    task = storage.update_task(1, "Updated Task", "New Desc", 2, 1)
    assert task is not None
    assert task.title == "Updated Task"
    assert task.column_id == 2