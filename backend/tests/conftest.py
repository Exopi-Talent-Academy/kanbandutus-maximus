import json
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.kanban import main
from src.kanban.storage import JsonStorage, SqlAlchemyStorage


def create_nested_data() -> dict:
    return {
        "boards": [
            {
                "id": 1,
                "name": "Test Board",
                "columns": [
                    {
                        "id": 1,
                        "name": "To Do",
                        "position": 0,
                        "board_id": 1,
                        "tasks": [
                            {
                                "id": 1,
                                "title": "Test Task",
                                "description": "Test description",
                                "assignee": "",
                                "column_id": 1,
                                "position": 0
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "name": "Done",
                        "position": 1,
                        "board_id": 1,
                        "tasks": []
                    }
                ]
            }
        ],
        "accounts": [
            {
                "id": 1,
                "username": "admin",
                "password_hash": "admin",
                "role": "admin"
            },
            {
                "id": 2,
                "username": "writer",
                "password_hash": "writer",
                "role": "write"
            },
            {
                "id": 4,
                "username": "guest",
                "password_hash": "guest",
                "role": "read"
            }
        ]
    }


@pytest.fixture
def temp_data_file() -> Generator[Path, None, None]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(create_nested_data(), f)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


@pytest.fixture
def json_storage(temp_data_file) -> JsonStorage:
    return JsonStorage(temp_data_file)


@pytest.fixture
def sqlalchemy_storage() -> Generator[SqlAlchemyStorage, None, None]:
    from sqlalchemy import text

    storage = SqlAlchemyStorage()

    with storage._session() as session:
        session.execute(text("DELETE FROM accounts"))
        session.execute(text("DELETE FROM tasks"))
        session.execute(text("DELETE FROM columns"))
        session.execute(text("DELETE FROM board"))
        session.commit()

        session.execute(text("INSERT INTO accounts (id, username, password_hash, role) VALUES (1, 'admin', 'admin', 'admin')"))
        session.execute(text("INSERT INTO accounts (id, username, password_hash, role) VALUES (2, 'writer', 'writer', 'write')"))
        session.execute(text("INSERT INTO accounts (id, username, password_hash, role) VALUES (4, 'guest', 'guest', 'read')"))
        session.execute(text("INSERT INTO board (id, name) VALUES (1, 'Test Board')"))
        session.execute(text("INSERT INTO columns (id, name, position, board_id) VALUES (1, 'To Do', 0, 1)"))
        session.execute(text("INSERT INTO columns (id, name, position, board_id) VALUES (2, 'Done', 1, 1)"))
        session.execute(text("INSERT INTO tasks (id, title, description, assignee, column_id, position) VALUES (1, 'Test Task', 'Test description', '', 1, 0)"))
        session.commit()

    yield storage

    with storage._session() as session:
        session.execute(text("DELETE FROM accounts"))
        session.execute(text("DELETE FROM tasks"))
        session.execute(text("DELETE FROM columns"))
        session.execute(text("DELETE FROM board"))
        session.commit()


@pytest.fixture(params=["json", "sqlalchemy"])
def storage(request, temp_data_file, sqlalchemy_storage) -> object:
    if request.param == "json":
        return JsonStorage(temp_data_file)
    else:
        return sqlalchemy_storage


@pytest.fixture
def client(temp_data_file, monkeypatch) -> TestClient:
    os.environ["KANBAN_STORAGE_BACKEND"] = "sqlite"

    from sqlalchemy import text
    from src.kanban.storage import SqlAlchemyStorage

    storage = SqlAlchemyStorage()

    with storage._session() as session:
        session.execute(text("DELETE FROM accounts"))
        session.execute(text("DELETE FROM tasks"))
        session.execute(text("DELETE FROM columns"))
        session.execute(text("DELETE FROM board"))
        session.commit()

        session.execute(text("INSERT INTO accounts (id, username, password_hash, role) VALUES (1, 'admin', 'admin', 'admin')"))
        session.execute(text("INSERT INTO accounts (id, username, password_hash, role) VALUES (2, 'writer', 'writer', 'write')"))
        session.execute(text("INSERT INTO accounts (id, username, password_hash, role) VALUES (4, 'guest', 'guest', 'read')"))
        session.execute(text("INSERT INTO board (id, name) VALUES (1, 'Test Board')"))
        session.execute(text("INSERT INTO columns (id, name, position, board_id) VALUES (1, 'To Do', 0, 1)"))
        session.execute(text("INSERT INTO columns (id, name, position, board_id) VALUES (2, 'Done', 1, 1)"))
        session.execute(text("INSERT INTO tasks (id, title, description, assignee, column_id, position) VALUES (1, 'Test Task', 'Test description', '', 1, 0)"))
        session.commit()

    main.service = main.KanbanService(storage)

    with TestClient(main.app) as c:
        yield c
