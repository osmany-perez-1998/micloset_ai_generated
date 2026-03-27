import pytest
from fastapi.testclient import TestClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

VALID_USER = {
    "full_name": "Ana Garcia",
    "email": "ana@example.com",
    "password": "SecurePass123",
    "phone": "+5351234567",
    "cuba_address": "Calle 23 #456",
    "cuba_city": "La Habana",
}


# ─── Register ────────────────────────────────────────────────────────────────

def test_register_success(client: TestClient):
    res = client.post(REGISTER_URL, json=VALID_USER)
    assert res.status_code == 201
    body = res.json()
    assert "access_token" in body
    assert body["user"]["email"] == VALID_USER["email"]
    assert body["user"]["role"] == "customer"


def test_register_duplicate_email(client: TestClient):
    client.post(REGISTER_URL, json=VALID_USER)
    res = client.post(REGISTER_URL, json=VALID_USER)
    assert res.status_code == 409


def test_register_invalid_email(client: TestClient):
    bad = {**VALID_USER, "email": "not-an-email"}
    res = client.post(REGISTER_URL, json=bad)
    assert res.status_code == 422


# ─── Login ───────────────────────────────────────────────────────────────────

def test_login_success(client: TestClient):
    client.post(REGISTER_URL, json=VALID_USER)
    res = client.post(LOGIN_URL, json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client: TestClient):
    client.post(REGISTER_URL, json=VALID_USER)
    res = client.post(LOGIN_URL, json={"email": VALID_USER["email"], "password": "wrong"})
    assert res.status_code == 401


def test_login_unknown_email(client: TestClient):
    res = client.post(LOGIN_URL, json={"email": "nobody@example.com", "password": "pass"})
    assert res.status_code == 401


# ─── /me ─────────────────────────────────────────────────────────────────────

def test_me_returns_current_user(client: TestClient):
    reg = client.post(REGISTER_URL, json=VALID_USER).json()
    token = reg["access_token"]
    res = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == VALID_USER["email"]


def test_me_no_token(client: TestClient):
    res = client.get(ME_URL)
    assert res.status_code == 403


def test_me_invalid_token(client: TestClient):
    res = client.get(ME_URL, headers={"Authorization": "Bearer garbage"})
    assert res.status_code == 401
