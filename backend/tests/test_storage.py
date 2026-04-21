import importlib
import json

import pytest

from src.kanban.models import Board, Column, Task


def test_get_board(storage):
    board = storage.get_board(1)
    assert board is not None
    assert board.name == "Test Board"
    assert len(board.columns) >= 1


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


def test_load_accounts(storage):
    data = storage.load()
    assert len(data.accounts) == 2
    assert data.accounts[0].username == "admin"


def test_get_account(storage):
    account = storage.get_account(1)
    assert account is not None
    assert account.username == "admin"
    assert account.password_hash == "admin"


def test_get_account_not_found(storage):
    account = storage.get_account(999)
    assert account is None


def test_create_board(storage):
    board = storage.create_board("New Board")
    assert board.id >= 2
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


def test_sqlite_db_is_created_and_seeded_from_json(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_file = data_dir / "kanban.json"
    db_file = data_dir / "kanban.db"

    sample_data = {
        "boards": [
            {
                "id": 1,
                "name": "Seed Board",
                "columns": [
                    {
                        "id": 1,
                        "name": "To Do",
                        "position": 0,
                        "board_id": 1,
                        "tasks": [
                            {
                                "id": 1,
                                "title": "Seed Task",
                                "description": "Loaded from JSON",
                                "assignee": "",
                                "column_id": 1,
                                "position": 0,
                            }
                        ],
                    }
                ],
            }
        ],
        "accounts": [
            {
                "id": 1,
                "username": "seed-admin",
                "password_hash": "seed-admin"
            }
        ]
    }
    data_file.write_text(json.dumps(sample_data), encoding="utf-8")

    monkeypatch.setenv("KANBAN_DATA_DIR", str(data_dir))
    monkeypatch.setenv("KANBAN_DATABASE_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("KANBAN_STORAGE_BACKEND", "sqlite")

    import src.kanban.config as config_module
    import src.kanban.db as db_module
    import src.kanban.storage as storage_module

    importlib.reload(config_module)
    importlib.reload(db_module)
    importlib.reload(storage_module)

    storage = storage_module.SqlAlchemyStorage()
    board = storage.get_board(1)
    task = storage.get_task(1)
    account = storage.get_account(1)

    assert db_file.exists()
    assert board is not None
    assert board.name == "Seed Board"
    assert task is not None
    assert task.title == "Seed Task"
    assert account is not None
    assert account.username == "seed-admin"

    monkeypatch.delenv("KANBAN_DATA_DIR", raising=False)
    monkeypatch.delenv("KANBAN_DATABASE_URL", raising=False)
    monkeypatch.delenv("KANBAN_STORAGE_BACKEND", raising=False)
    importlib.reload(config_module)
    importlib.reload(db_module)
    importlib.reload(storage_module)
