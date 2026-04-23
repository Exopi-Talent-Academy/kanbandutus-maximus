# ============================================================================
# Layer 3: API Endpoint Tests
# ============================================================================
# Tests for all REST API endpoints organized by entity category.
# These tests hit the API layer which calls the service layer.
# ============================================================================

from src.kanban.storage import SqlAlchemyStorage


WRITE_HEADERS = {"X-Demo-Account-Id": "1"}
READ_HEADERS = {"X-Demo-Account-Id": "3"}


# ============================================================================
# Section 1: Boards
# ============================================================================

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


# ============================================================================
# Section 2: Columns
# ============================================================================

def test_create_column_success(client):
    response = client.post(
        "/api/columns",
        json={"name": "In Progress", "position": 2, "board_id": 1},
        headers=WRITE_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "In Progress"
    assert data["position"] == 2
    assert data["board_id"] == 1

    board_response = client.get("/api/boards/1")
    assert board_response.status_code == 200
    board = board_response.json()
    column_names = [column["name"] for column in board["columns"]]
    assert "In Progress" in column_names


def test_create_column_invalid_board(client):
    response = client.post(
        "/api/columns",
        json={"name": "Blocked", "position": 0, "board_id": 999},
        headers=WRITE_HEADERS,
    )

    assert response.status_code == 404


def test_update_column_success(client):
    response = client.put(
        "/api/columns/1",
        json={"name": "Ready", "position": 3},
        headers=WRITE_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Ready"
    assert data["position"] == 1

    board_response = client.get("/api/boards/1")
    assert board_response.status_code == 200
    board = board_response.json()
    updated_column = next(column for column in board["columns"] if column["id"] == 1)
    assert updated_column["name"] == "Ready"
    assert updated_column["position"] == 1


def test_update_column_invalid_column_id(client):
    response = client.put(
        "/api/columns/999",
        json={"name": "Ready", "position": 3},
        headers=WRITE_HEADERS,
    )

    assert response.status_code == 404


def test_delete_column_success(client):
    response = client.delete("/api/columns/1", headers=WRITE_HEADERS)

    assert response.status_code == 200
    assert response.json() == {"message": "Column deleted"}

    board_response = client.get("/api/boards/1")
    assert board_response.status_code == 200
    board = board_response.json()
    column_ids = [column["id"] for column in board["columns"]]
    task_ids = [task["id"] for column in board["columns"] for task in column["tasks"]]
    assert 1 not in column_ids
    assert 1 not in task_ids


def test_delete_column_invalid_column_id(client):
    response = client.delete("/api/columns/999", headers=WRITE_HEADERS)


def test_create_column_rejects_read_only_account(client):
    response = client.post(
        "/api/columns",
        json={"name": "Blocked", "position": 0, "board_id": 1},
        headers=READ_HEADERS,
    )

    assert response.status_code == 403


# ============================================================================
# Section 3: Tasks
# ============================================================================

def test_create_task_success(client):
    response = client.post("/api/tasks", json={
        "title": "New Task",
        "description": "Task description",
        "column_id": 1,
        "position": 0
    }, headers=WRITE_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Task"
    assert data["column_id"] == 1


def test_create_task_invalid_column(client):
    response = client.post("/api/tasks", json={
        "title": "New Task",
        "description": "Task description",
        "column_id": 999,
        "position": 0
    }, headers=WRITE_HEADERS)
    assert response.status_code == 404


def test_update_task_success(client):
    response = client.put("/api/tasks/1", json={
        "title": "Updated Task",
        "description": "Updated description",
        "column_id": 2,
        "position": 1
    }, headers=WRITE_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["column_id"] == 2


def test_update_task_invalid_task_id(client):
    response = client.put("/api/tasks/999", json={
        "title": "Updated Task",
        "description": "Updated description",
        "column_id": 1,
        "position": 0
    }, headers=WRITE_HEADERS)
    assert response.status_code == 404


def test_update_task_invalid_column(client):
    response = client.put("/api/tasks/1", json={
        "title": "Updated Task",
        "description": "Updated description",
        "column_id": 999,
        "position": 0
    }, headers=WRITE_HEADERS)
    assert response.status_code == 404


def test_update_task_reorders_positions_across_columns(client):
    source_response = client.post("/api/tasks", json={
        "title": "Second Task",
        "description": "Task description",
        "column_id": 1,
        "position": 1
    }, headers=WRITE_HEADERS)
    target_response = client.post("/api/tasks", json={
        "title": "Done Task",
        "description": "Task description",
        "column_id": 2,
        "position": 0
    }, headers=WRITE_HEADERS)

    assert source_response.status_code == 200
    assert target_response.status_code == 200

    moved_task_id = source_response.json()["id"]
    existing_target_task_id = target_response.json()["id"]

    response = client.put(f"/api/tasks/{moved_task_id}", json={
        "title": "Second Task",
        "description": "Task description",
        "column_id": 2,
        "position": 0
    }, headers=WRITE_HEADERS)

    assert response.status_code == 200
    assert response.json()["position"] == 0

    board_response = client.get("/api/boards/1")

    assert board_response.status_code == 200

    board = board_response.json()
    todo_column = next(column for column in board["columns"] if column["id"] == 1)
    done_column = next(column for column in board["columns"] if column["id"] == 2)

    assert [task["id"] for task in todo_column["tasks"]] == [1]
    assert [task["position"] for task in todo_column["tasks"]] == [0]
    assert [task["id"] for task in done_column["tasks"]] == [moved_task_id, existing_target_task_id]
    assert [task["position"] for task in done_column["tasks"]] == [0, 1]


def test_delete_task_success(client):
    response = client.delete("/api/tasks/1", headers=WRITE_HEADERS)

    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted"}

    storage = SqlAlchemyStorage()
    assert storage.get_task(1) is None

    board_response = client.get("/api/boards/1")
    assert board_response.status_code == 200
    board = board_response.json()
    all_task_ids = [task["id"] for column in board["columns"] for task in column["tasks"]]
    assert 1 not in all_task_ids


def test_delete_task_invalid_task_id(client):
    response = client.delete("/api/tasks/999", headers=WRITE_HEADERS)

    assert response.status_code == 404


# ============================================================================
# Section 4: Accounts
# ============================================================================

def test_get_accounts_returns_list(client):
    response = client.get("/api/accounts")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["username"] == "admin"
    assert data[0]["role"] == "admin"
    assert "password_hash" not in data[0]


def test_get_account_success(client):
    response = client.get("/api/accounts/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "admin"
    assert data["role"] == "admin"
    assert "password_hash" not in data


def test_get_account_not_found(client):
    response = client.get("/api/accounts/999")

    assert response.status_code == 404