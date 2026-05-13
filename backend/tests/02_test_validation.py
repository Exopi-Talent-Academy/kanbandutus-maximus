import pytest
from fastapi.testclient import TestClient


# Empty String Rejection Tests (will fail)


def test_create_column_rejects_empty_name(client):
    response = client.post(
        "/api/columns",
        json={"name": "", "position": 0, "board_id": 1},
    )
    assert response.status_code == 422


def test_update_column_rejects_empty_name(client):
    response = client.put(
        "/api/columns/1",
        json={"name": "", "position": 0},
    )
    assert response.status_code == 422


def test_create_task_rejects_empty_title(client):
    response = client.post(
        "/api/tasks",
        json={"title": "", "description": "", "column_id": 1, "position": 0},
    )
    assert response.status_code == 422


def test_update_task_rejects_empty_title(client):
    response = client.put(
        "/api/tasks/1",
        json={"title": "", "description": "", "column_id": 1, "position": 0},
    )
    assert response.status_code == 422


# Negative Position Rejection Tests (will fail)


def test_create_column_rejects_negative_position(client):
    response = client.post(
        "/api/columns",
        json={"name": "Test Column", "position": -1, "board_id": 1},
    )
    assert response.status_code == 422


def test_update_column_rejects_negative_position(client):
    response = client.put(
        "/api/columns/1",
        json={"name": "Test Column", "position": -1},
    )
    assert response.status_code == 422


def test_create_task_rejects_negative_position(client):
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "", "column_id": 1, "position": -1},
    )
    assert response.status_code == 422


def test_update_task_rejects_negative_position(client):
    response = client.put(
        "/api/tasks/1",
        json={"title": "Test Task", "description": "", "column_id": 1, "position": -1},
    )
    assert response.status_code == 422


# Wrong Type Rejection Tests (will pass)


def test_create_column_rejects_numeric_name(client):
    response = client.post(
        "/api/columns",
        json={"name": 123, "position": 0, "board_id": 1},
    )
    assert response.status_code == 422


def test_create_column_rejects_string_position(client):
    response = client.post(
        "/api/columns",
        json={"name": "Test Column", "position": "abc", "board_id": 1},
    )
    assert response.status_code == 422


def test_create_task_rejects_numeric_title(client):
    response = client.post(
        "/api/tasks",
        json={"title": 123, "description": "", "column_id": 1, "position": 0},
    )
    assert response.status_code == 422


def test_create_task_rejects_string_column_id(client):
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "", "column_id": "abc", "position": 0},
    )
    assert response.status_code == 422


# Missing Required Fields Tests (will pass)


def test_create_column_requires_name(client):
    response = client.post(
        "/api/columns",
        json={"position": 0, "board_id": 1},
    )
    assert response.status_code == 422


def test_create_task_requires_title(client):
    response = client.post(
        "/api/tasks",
        json={"description": "", "column_id": 1, "position": 0},
    )
    assert response.status_code == 422