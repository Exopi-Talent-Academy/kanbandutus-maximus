def test_get_accounts_returns_list(client):
    response = client.get("/api/accounts")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["username"] == "admin"


def test_get_account_success(client):
    response = client.get("/api/accounts/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "admin"


def test_get_account_not_found(client):
    response = client.get("/api/accounts/999")

    assert response.status_code == 404