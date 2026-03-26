"""Tests for authentication endpoints."""


def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"phone": "+5355551234", "name": "Ana García", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["phone"] == "+5355551234"
    assert data["user"]["role"] == "CUSTOMER"


def test_register_duplicate_phone(client):
    payload = {"phone": "+5355551234", "name": "Ana García", "password": "secret123"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"phone": "+5355551234", "name": "Ana García", "password": "secret123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "+5355551234", "password": "secret123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"phone": "+5355551234", "name": "Ana García", "password": "secret123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "+5355551234", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_get_me(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"phone": "+5355551234", "name": "Ana García", "password": "secret123"},
    )
    token = reg.json()["access_token"]
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Ana García"
