import pytest


def test_get_tasks_by_column_success(client):
    response = client.get("/api/columns/1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Test Task"
    assert data[0]["column_id"] == 1


def test_get_tasks_by_column_empty(client):
    response = client.get("/api/columns/2/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_tasks_by_column_not_found(client):
    response = client.get("/api/columns/999/tasks")
    assert response.status_code == 404
