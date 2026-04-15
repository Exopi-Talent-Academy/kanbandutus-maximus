import pytest


def test_get_boards_returns_list(client):
    response = client.get("/api/boards")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_boards_empty(temp_data_file, monkeypatch):
    import json
    from src.kanban import main, storage as storage_module

    with open(temp_data_file, "w") as f:
        json.dump({"boards": [], "columns": [], "tasks": []}, f)

    s = storage_module.JsonStorage(temp_data_file)
    main.service = main.KanbanService(s)

    from fastapi.testclient import TestClient
    with TestClient(main.app) as c:
        response = c.get("/api/boards")
        assert response.status_code == 200
        assert response.json() == []


def test_get_board_success(client):
    response = client.get("/api/boards/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Board"


def test_get_board_not_found(client):
    response = client.get("/api/boards/999")
    assert response.status_code == 404