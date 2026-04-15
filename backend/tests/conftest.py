import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.kanban import config, main
from src.kanban.storage import JsonStorage


@pytest.fixture
def temp_data_file() -> Generator[Path, None, None]:
    data = {
        "boards": [{"id": 1, "name": "Test Board", "columns": [1, 2]}],
        "columns": [
            {"id": 1, "name": "To Do", "position": 0, "board_id": 1},
            {"id": 2, "name": "Done", "position": 1, "board_id": 1}
        ],
        "tasks": [{"id": 1, "title": "Test Task", "description": "Test", "column_id": 1, "position": 0}]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


@pytest.fixture
def storage(temp_data_file) -> JsonStorage:
    return JsonStorage(temp_data_file)


@pytest.fixture
def client(temp_data_file, monkeypatch):
    def override_get_data_file() -> Path:
        return temp_data_file

    monkeypatch.setattr(config, "get_data_file", override_get_data_file)

    storage = JsonStorage(temp_data_file)
    main.service = main.KanbanService(storage)

    with TestClient(main.app) as c:
        yield c