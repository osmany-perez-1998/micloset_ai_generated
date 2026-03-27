"""
Tests for MC-004: Estimate Engine
  - GET /orders/{id}/fetch-prices
  - POST /orders/{id}/estimate
  - POST /orders/{id}/payment
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ORDERS_URL = "/api/v1/orders"

# ─── Test users ──────────────────────────────────────────────────────────────

CUSTOMER = {"full_name": "Ana García", "email": "ana@example.com", "password": "Pass1234"}
REP_DATA = {"full_name": "Rep Staff", "email": "rep@micloset.com", "password": "Staff5678"}

VALID_ORDER = {
    "items": [
        {"product_url": "https://www.amazon.com/dp/B08N5WRWNW", "quantity": 1},
        {"product_url": "https://www.shein.com/p/dress-1234.html", "quantity": 2},
    ],
    "shipping_method": "standard_air",
    "delivery_preference": "home_delivery",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _register(client, data: dict) -> dict:
    return client.post(REGISTER_URL, json=data).json()


def _login_token(client, email: str, password: str) -> str:
    resp = client.post(LOGIN_URL, data={"username": email, "password": password})
    return resp.json()["access_token"]


def _make_rep(client: TestClient, db) -> str:
    """Register a user and elevate to sales_rep in the DB, return their token."""
    from app.models.user import User, UserRole
    res = _register(client, REP_DATA)
    user_id = res["user"]["id"]
    user = db.query(User).filter(User.id == user_id).first()
    user.role = UserRole.SALES_REP
    db.commit()
    return res["access_token"]


def _create_order(client, token: str) -> str:
    resp = client.post(
        ORDERS_URL,
        json=VALID_ORDER,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()["id"]


def _get_item_ids(client, order_id: str, rep_token: str) -> list[str]:
    resp = client.get(
        f"{ORDERS_URL}/{order_id}",
        headers={"Authorization": f"Bearer {rep_token}"},
    )
    return [item["id"] for item in resp.json()["items"]]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ─── Fake scraper coroutine ──────────────────────────────────────────────────

async def _fake_fetch(url: str):
    from app.services.price_scraper import PriceResult
    return PriceResult(
        url=url, price=25.99, currency="USD",
        store="amazon.com", method="json-ld", raw_text=None, needs_manual=False,
    )


async def _failed_fetch(url: str):
    from app.services.price_scraper import PriceResult
    return PriceResult(
        url=url, price=None, currency=None,
        store=None, method=None, raw_text=None, needs_manual=True,
    )


# ─── Tests: fetch-prices ─────────────────────────────────────────────────────

class TestFetchPrices:
    def test_staff_can_fetch_prices(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)

        with patch("app.services.estimate.fetch_price", side_effect=_fake_fetch):
            resp = client.get(
                f"{ORDERS_URL}/{order_id}/fetch-prices",
                headers=auth(rep_token),
            )

        assert resp.status_code == 200
        body = resp.json()
        assert len(body["results"]) == 2
        assert body["all_found"] is True
        assert body["results"][0]["price"] == 25.99
        assert body["results"][0]["method"] == "json-ld"

    def test_customer_cannot_fetch_prices(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        _make_rep(client, db)
        order_id = _create_order(client, cust_token)

        resp = client.get(
            f"{ORDERS_URL}/{order_id}/fetch-prices",
            headers=auth(cust_token),
        )
        assert resp.status_code == 403

    def test_fetch_prices_unauthenticated(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        order_id = _create_order(client, cust_token)

        resp = client.get(f"{ORDERS_URL}/{order_id}/fetch-prices")
        assert resp.status_code in (401, 403)

    def test_needs_manual_when_scraper_fails(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)

        with patch("app.services.estimate.fetch_price", side_effect=_failed_fetch):
            resp = client.get(
                f"{ORDERS_URL}/{order_id}/fetch-prices",
                headers=auth(rep_token),
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["all_found"] is False
        assert all(r["needs_manual"] is True for r in body["results"])


# ─── Tests: submit estimate ──────────────────────────────────────────────────

class TestSubmitEstimate:
    def _submit(self, client, order_id, item_ids, fee_pct, token):
        return client.post(
            f"{ORDERS_URL}/{order_id}/estimate",
            json={
                "item_prices": [{"order_item_id": iid, "price_usd": 25.99} for iid in item_ids],
                "service_fee_pct": fee_pct,
            },
            headers=auth(token),
        )

    def test_valid_estimate_accepted(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)
        item_ids = _get_item_ids(client, order_id, rep_token)

        resp = self._submit(client, order_id, item_ids, 10, rep_token)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "estimate_provided"
        # subtotal = 25.99 * 1 + 25.99 * 2 = 77.97
        assert body["subtotal_usd"] == pytest.approx(77.97, abs=0.01)
        # fee = 77.97 * 10% = 7.797 → 7.80
        assert body["service_fee_usd"] == pytest.approx(7.80, abs=0.01)
        assert body["total_estimate_usd"] == pytest.approx(85.77, abs=0.01)

    def test_zero_fee_accepted(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)
        item_ids = _get_item_ids(client, order_id, rep_token)

        resp = self._submit(client, order_id, item_ids, 0, rep_token)
        assert resp.status_code == 200
        assert resp.json()["service_fee_usd"] == 0.0

    def test_invalid_fee_tier_rejected(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)
        item_ids = _get_item_ids(client, order_id, rep_token)

        resp = self._submit(client, order_id, item_ids, 5, rep_token)  # 5 not in tiers
        assert resp.status_code == 422

    def test_all_valid_fee_tiers_accepted(self, client, db):
        from app.models.user import User, UserRole
        for i, fee in enumerate([0, 7, 10, 15, 17, 20]):
            cust = {"full_name": "C", "email": f"c{fee}x{i}@x.com", "password": "Pass1234"}
            cust_token = _register(client, cust)["access_token"]
            order_id = _create_order(client, cust_token)

            rep_data = {"full_name": "R", "email": f"r{fee}x{i}@x.com", "password": "Pass1234"}
            res = _register(client, rep_data)
            user = db.query(User).filter(User.id == res["user"]["id"]).first()
            user.role = UserRole.SALES_REP
            db.commit()
            rep_token = res["access_token"]

            item_ids = _get_item_ids(client, order_id, rep_token)
            resp = self._submit(client, order_id, item_ids, fee, rep_token)
            assert resp.status_code == 200, f"Fee {fee}% rejected: {resp.json()}"

    def test_customer_cannot_submit_estimate(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)
        item_ids = _get_item_ids(client, order_id, rep_token)

        resp = self._submit(client, order_id, item_ids, 10, cust_token)
        assert resp.status_code == 403

    def test_missing_item_price_rejected(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)
        item_ids = _get_item_ids(client, order_id, rep_token)

        # Provide price for only the first item
        resp = client.post(
            f"{ORDERS_URL}/{order_id}/estimate",
            json={
                "item_prices": [{"order_item_id": item_ids[0], "price_usd": 25.99}],
                "service_fee_pct": 10,
            },
            headers=auth(rep_token),
        )
        assert resp.status_code == 422

    def test_estimate_on_nonexistent_order_returns_404(self, client, db):
        rep_token = _make_rep(client, db)
        resp = client.post(
            f"{ORDERS_URL}/nonexistent-id/estimate",
            json={"item_prices": [], "service_fee_pct": 10},
            headers=auth(rep_token),
        )
        assert resp.status_code == 404


# ─── Tests: record payment ───────────────────────────────────────────────────

class TestRecordPayment:
    def _setup_estimate(self, client, db):
        """Create order + submit estimate. Returns (order_id, cust_token, rep_token)."""
        cust_token = _register(client, CUSTOMER)["access_token"]
        rep_token = _make_rep(client, db)
        order_id = _create_order(client, cust_token)
        item_ids = _get_item_ids(client, order_id, rep_token)

        client.post(
            f"{ORDERS_URL}/{order_id}/estimate",
            json={
                "item_prices": [{"order_item_id": iid, "price_usd": 25.99} for iid in item_ids],
                "service_fee_pct": 10,
            },
            headers=auth(rep_token),
        )
        return order_id, cust_token, rep_token

    def test_deposit_payment_accepted(self, client, db):
        order_id, cust_token, _ = self._setup_estimate(client, db)

        resp = client.post(
            f"{ORDERS_URL}/{order_id}/payment",
            json={"payment_type": "deposit", "amount_usd": 42.89, "payment_method": "cash"},
            headers=auth(cust_token),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "deposit_paid"
        assert body["deposit_paid_usd"] == pytest.approx(42.89, abs=0.01)
        assert body["deposit_payment_method"] == "cash"

    def test_full_prepay_accepted(self, client, db):
        order_id, cust_token, _ = self._setup_estimate(client, db)

        resp = client.post(
            f"{ORDERS_URL}/{order_id}/payment",
            json={"payment_type": "full_prepay", "amount_usd": 85.77, "payment_method": "wire_transfer"},
            headers=auth(cust_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "deposit_paid"

    def test_payment_blocked_without_estimate(self, client, db):
        cust_token = _register(client, CUSTOMER)["access_token"]
        order_id = _create_order(client, cust_token)

        resp = client.post(
            f"{ORDERS_URL}/{order_id}/payment",
            json={"payment_type": "deposit", "amount_usd": 50.0, "payment_method": "cash"},
            headers=auth(cust_token),
        )
        assert resp.status_code == 409

    def test_invalid_payment_type_rejected(self, client, db):
        order_id, cust_token, _ = self._setup_estimate(client, db)

        resp = client.post(
            f"{ORDERS_URL}/{order_id}/payment",
            json={"payment_type": "wire", "amount_usd": 50.0, "payment_method": "cash"},
            headers=auth(cust_token),
        )
        assert resp.status_code == 422

    def test_invalid_payment_method_rejected(self, client, db):
        order_id, cust_token, _ = self._setup_estimate(client, db)

        resp = client.post(
            f"{ORDERS_URL}/{order_id}/payment",
            json={"payment_type": "deposit", "amount_usd": 50.0, "payment_method": "crypto"},
            headers=auth(cust_token),
        )
        assert resp.status_code == 422

    def test_unauthenticated_payment_rejected(self, client, db):
        order_id, _, _ = self._setup_estimate(client, db)

        resp = client.post(
            f"{ORDERS_URL}/{order_id}/payment",
            json={"payment_type": "deposit", "amount_usd": 50.0, "payment_method": "cash"},
        )
        assert resp.status_code in (401, 403)

    def test_rep_can_record_payment_on_behalf(self, client, db):
        """Staff can record payment — they receive cash in person."""
        order_id, _, rep_token = self._setup_estimate(client, db)

        resp = client.post(
            f"{ORDERS_URL}/{order_id}/payment",
            json={"payment_type": "deposit", "amount_usd": 42.89, "payment_method": "cash"},
            headers=auth(rep_token),
        )
        assert resp.status_code == 200
