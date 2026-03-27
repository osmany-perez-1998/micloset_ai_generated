import pytest
from fastapi.testclient import TestClient
from app.models.user import UserRole
from app.database import get_db

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ORDERS_URL = "/api/v1/orders"

CUSTOMER = {"full_name": "Cliente Test", "email": "cliente@test.com", "password": "Pass1234"}
REP = {"full_name": "Rep Test", "email": "rep@test.com", "password": "Pass1234"}

VALID_ORDER = {
    "items": [{"product_url": "https://amazon.com/dp/B001", "quantity": 1}],
    "shipping_method": "standard_air",
}


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_rep(client: TestClient, db) -> str:
    """Register a user and manually elevate to sales_rep role."""
    from app.models.user import User
    res = client.post(REGISTER_URL, json=REP)
    token = res.json()["access_token"]
    user_id = res.json()["user"]["id"]
    user = db.query(User).filter(User.id == user_id).first()
    user.role = UserRole.SALES_REP
    db.commit()
    # Re-login to get a token with the updated role in the DB
    return token  # existing token still valid (role checked from DB)


# ─── Staff list all orders ────────────────────────────────────────────────────

def test_staff_can_see_all_orders(client: TestClient, db):
    # Customer creates an order
    cust_token = client.post(REGISTER_URL, json=CUSTOMER).json()["access_token"]
    client.post(ORDERS_URL, json=VALID_ORDER, headers=auth(cust_token))

    rep_token = _make_rep(client, db)
    res = client.get(ORDERS_URL, headers=auth(rep_token))
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_staff_filter_by_status(client: TestClient, db):
    cust_token = client.post(REGISTER_URL, json=CUSTOMER).json()["access_token"]
    client.post(ORDERS_URL, json=VALID_ORDER, headers=auth(cust_token))

    rep_token = _make_rep(client, db)
    res = client.get(f"{ORDERS_URL}?status=links_submitted", headers=auth(rep_token))
    assert res.status_code == 200
    assert all(o["status"] == "links_submitted" for o in res.json())


def test_staff_filter_mine_empty_before_assignment(client: TestClient, db):
    cust_token = client.post(REGISTER_URL, json=CUSTOMER).json()["access_token"]
    client.post(ORDERS_URL, json=VALID_ORDER, headers=auth(cust_token))

    rep_token = _make_rep(client, db)
    res = client.get(f"{ORDERS_URL}?mine=true", headers=auth(rep_token))
    assert res.status_code == 200
    assert res.json() == []


# ─── Assign order ─────────────────────────────────────────────────────────────

def test_rep_can_assign_themselves(client: TestClient, db):
    cust_token = client.post(REGISTER_URL, json=CUSTOMER).json()["access_token"]
    order_id = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth(cust_token)).json()["id"]

    rep_token = _make_rep(client, db)
    res = client.patch(f"{ORDERS_URL}/{order_id}/assign", headers=auth(rep_token))
    assert res.status_code == 200
    assert res.json()["sales_rep"]["email"] == REP["email"]


def test_mine_filter_shows_assigned_orders(client: TestClient, db):
    cust_token = client.post(REGISTER_URL, json=CUSTOMER).json()["access_token"]
    order_id = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth(cust_token)).json()["id"]

    rep_token = _make_rep(client, db)
    client.patch(f"{ORDERS_URL}/{order_id}/assign", headers=auth(rep_token))

    res = client.get(f"{ORDERS_URL}?mine=true", headers=auth(rep_token))
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_customer_cannot_call_assign(client: TestClient):
    cust_token = client.post(REGISTER_URL, json=CUSTOMER).json()["access_token"]
    order_id = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth(cust_token)).json()["id"]
    res = client.patch(f"{ORDERS_URL}/{order_id}/assign", headers=auth(cust_token))
    assert res.status_code == 403


def test_assign_nonexistent_order(client: TestClient, db):
    rep_token = _make_rep(client, db)
    res = client.patch(f"{ORDERS_URL}/bad-id/assign", headers=auth(rep_token))
    assert res.status_code == 404
