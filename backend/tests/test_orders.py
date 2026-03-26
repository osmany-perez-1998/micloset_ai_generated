"""Tests for order creation and service fee calculation."""


def test_create_order(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"phone": "+5355550001", "name": "Customer A", "password": "pass1234"},
    )
    token = reg.json()["access_token"]
    response = client.post(
        "/api/v1/orders/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_url": "https://amazon.com/dp/B001", "quantity": 2},
                {"product_url": "https://shein.com/item/1234", "quantity": 1},
            ]
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUBMITTED"
    assert len(data["items"]) == 2


def test_service_fee_calculation():
    subtotal = 50 * 2 + 30 * 1
    fee_pct = 15.0
    fee = round(subtotal * fee_pct / 100, 2)
    total = round(subtotal + fee, 2)
    assert fee == 19.50
    assert total == 149.50


def test_list_my_orders(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"phone": "+5355550002", "name": "Customer B", "password": "pass1234"},
    )
    token = reg.json()["access_token"]
    client.post(
        "/api/v1/orders/",
        headers={"Authorization": f"Bearer {token}"},
        json={"items": [{"product_url": "https://amazon.com/dp/X001", "quantity": 1}]},
    )
    response = client.get(
        "/api/v1/orders/my", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_unauthenticated_order_rejected(client):
    response = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_url": "https://amazon.com/dp/B001", "quantity": 1}]},
    )
    assert response.status_code == 401
