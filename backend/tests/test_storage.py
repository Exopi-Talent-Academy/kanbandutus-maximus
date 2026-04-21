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
    assert column.position == 1

    board = storage.get_board(1)
    assert board is not None
    assert [item.id for item in board.columns] == [2, 1]
    assert [item.position for item in board.columns] == [0, 1]


def test_update_column_reorders_positions_within_board(storage):
    third_column = storage.create_column("Review", 2, 1)

    assert third_column is not None

    updated_column = storage.update_column(third_column.id, "Review", 0)

    assert updated_column is not None
    assert updated_column.position == 0

    board = storage.get_board(1)
    assert board is not None
    assert [item.id for item in board.columns] == [third_column.id, 1, 2]
    assert [item.position for item in board.columns] == [0, 1, 2]


def test_update_task(storage):
    task = storage.update_task(1, "Updated Task", "New Desc", 2, 1)
    assert task is not None
    assert task.title == "Updated Task"
    assert task.column_id == 2


def test_update_task_reorders_positions_within_same_column(storage):
    second_task = storage.create_task("Second Task", "", 1, 1)
    third_task = storage.create_task("Third Task", "", 1, 2)

    assert second_task is not None
    assert third_task is not None

    updated_task = storage.update_task(third_task.id, "Third Task", "", 1, 0)

    assert updated_task is not None

    column = storage.get_column(1)
    assert column is not None
    assert [task.id for task in column.tasks] == [third_task.id, 1, second_task.id]
    assert [task.position for task in column.tasks] == [0, 1, 2]


def test_update_task_reorders_positions_across_both_columns(storage):
    second_task = storage.create_task("Second Task", "", 1, 1)
    done_task = storage.create_task("Done Task", "", 2, 0)
    later_done_task = storage.create_task("Later Done Task", "", 2, 1)

    assert second_task is not None
    assert done_task is not None
    assert later_done_task is not None

    updated_task = storage.update_task(second_task.id, "Second Task", "", 2, 1)

    assert updated_task is not None
    assert updated_task.column_id == 2
    assert updated_task.position == 1

    source_column = storage.get_column(1)
    target_column = storage.get_column(2)

    assert source_column is not None
    assert target_column is not None
    assert [task.id for task in source_column.tasks] == [1]
    assert [task.position for task in source_column.tasks] == [0]
    assert [task.id for task in target_column.tasks] == [done_task.id, second_task.id, later_done_task.id]
    assert [task.position for task in target_column.tasks] == [0, 1, 2]


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

    assert db_file.exists()
    assert board is not None
    assert board.name == "Seed Board"
    assert task is not None
    assert task.title == "Seed Task"

    monkeypatch.delenv("KANBAN_DATA_DIR", raising=False)
    monkeypatch.delenv("KANBAN_DATABASE_URL", raising=False)
    monkeypatch.delenv("KANBAN_STORAGE_BACKEND", raising=False)
    importlib.reload(config_module)
    importlib.reload(db_module)
    importlib.reload(storage_module)
