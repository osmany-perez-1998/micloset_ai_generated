import pytest
from fastapi.testclient import TestClient

REGISTER_URL = "/api/v1/auth/register"
ORDERS_URL = "/api/v1/orders"

CUSTOMER = {
    "full_name": "Maria Lopez",
    "email": "maria@example.com",
    "password": "Pass1234",
}

VALID_ORDER = {
    "items": [
        {
            "product_url": "https://www.amazon.com/dp/B08N5WRWNW",
            "quantity": 1,
            "size": "M",
            "color": "Negro",
        },
        {
            "product_url": "https://www.shein.com/p/some-dress-p-1234567.html",
            "quantity": 2,
        },
    ],
    "shipping_method": "standard_air",
    "delivery_preference": "home_delivery",
    "customer_notes": "Por favor empacar bien.",
}


def _register_and_token(client: TestClient) -> str:
    res = client.post(REGISTER_URL, json=CUSTOMER)
    assert res.status_code == 201
    return res.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ─── Create order ─────────────────────────────────────────────────────────────

def test_create_order_success(client: TestClient):
    token = _register_and_token(client)
    res = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth_header(token))
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "links_submitted"
    assert body["order_number"].startswith("MC-")
    assert len(body["items"]) == 2


def test_create_order_number_is_unique(client: TestClient):
    token = _register_and_token(client)
    r1 = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth_header(token))
    r2 = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth_header(token))
    assert r1.json()["order_number"] != r2.json()["order_number"]


def test_create_order_no_items_rejected(client: TestClient):
    token = _register_and_token(client)
    res = client.post(ORDERS_URL, json={"items": []}, headers=auth_header(token))
    assert res.status_code == 422


def test_create_order_requires_auth(client: TestClient):
    res = client.post(ORDERS_URL, json=VALID_ORDER)
    assert res.status_code == 403


# ─── List orders ──────────────────────────────────────────────────────────────

def test_list_orders_returns_only_own(client: TestClient):
    token = _register_and_token(client)
    client.post(ORDERS_URL, json=VALID_ORDER, headers=auth_header(token))
    client.post(ORDERS_URL, json=VALID_ORDER, headers=auth_header(token))

    res = client.get(ORDERS_URL, headers=auth_header(token))
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_orders_empty_for_new_customer(client: TestClient):
    token = _register_and_token(client)
    res = client.get(ORDERS_URL, headers=auth_header(token))
    assert res.status_code == 200
    assert res.json() == []


# ─── Get order detail ─────────────────────────────────────────────────────────

def test_get_order_detail_success(client: TestClient):
    token = _register_and_token(client)
    order_id = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth_header(token)).json()["id"]

    res = client.get(f"{ORDERS_URL}/{order_id}", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json()["id"] == order_id


def test_get_order_detail_not_found(client: TestClient):
    token = _register_and_token(client)
    res = client.get(f"{ORDERS_URL}/nonexistent-id", headers=auth_header(token))
    assert res.status_code == 404


def test_customer_cannot_access_another_customers_order(client: TestClient):
    token_a = _register_and_token(client)
    order_id = client.post(ORDERS_URL, json=VALID_ORDER, headers=auth_header(token_a)).json()["id"]

    # Register a second customer
    token_b = client.post(REGISTER_URL, json={**CUSTOMER, "email": "other@example.com"}).json()[
        "access_token"
    ]
    res = client.get(f"{ORDERS_URL}/{order_id}", headers=auth_header(token_b))
    assert res.status_code == 403
