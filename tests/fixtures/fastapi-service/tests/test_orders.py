from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_orders_require_key():
    assert client.get("/orders").status_code == 422


def test_unknown_order():
    r = client.get("/orders/999", headers={"x-api-key": "test"})
    assert r.status_code in (401, 404)
