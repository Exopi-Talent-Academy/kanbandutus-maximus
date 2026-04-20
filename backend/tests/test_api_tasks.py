from src.kanban.storage import SqlAlchemyStorage


def test_create_task_success(client):
    response = client.post("/api/tasks", json={
        "title": "New Task",
        "description": "Task description",
        "column_id": 1,
        "position": 0
    })
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
    })
    assert response.status_code == 404


def test_update_task_success(client):
    response = client.put("/api/tasks/1", json={
        "title": "Updated Task",
        "description": "Updated description",
        "column_id": 2,
        "position": 1
    })
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
    })
    assert response.status_code == 404


def test_update_task_invalid_column(client):
    response = client.put("/api/tasks/1", json={
        "title": "Updated Task",
        "description": "Updated description",
        "column_id": 999,
        "position": 0
    })
    assert response.status_code == 404


def test_delete_task_success(client):
    response = client.delete("/api/tasks/1")

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
    response = client.delete("/api/tasks/999")

    assert response.status_code == 404