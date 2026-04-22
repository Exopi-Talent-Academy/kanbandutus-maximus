def test_create_column_success(client):
    response = client.post(
        "/api/columns",
        json={"name": "In Progress", "position": 2, "board_id": 1},
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
    )

    assert response.status_code == 404


def test_update_column_success(client):
    response = client.put(
        "/api/columns/1",
        json={"name": "Ready", "position": 3},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Ready"
    assert data["position"] == 3

    board_response = client.get("/api/boards/1")
    assert board_response.status_code == 200
    board = board_response.json()
    updated_column = next(column for column in board["columns"] if column["id"] == 1)
    assert updated_column["name"] == "Ready"
    assert updated_column["position"] == 3


def test_update_column_invalid_column_id(client):
    response = client.put(
        "/api/columns/999",
        json={"name": "Ready", "position": 3},
    )

    assert response.status_code == 404


def test_delete_column_success(client):
    response = client.delete("/api/columns/1")

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
    response = client.delete("/api/columns/999")

    assert response.status_code == 404
