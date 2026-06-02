"""
API Integration Tests — requires a running test database.
Run with: pytest tests/ -v
Set TEST_DATABASE_URL env var to point to a test DB.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/inventory_test_db",
)

engine_test = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import OrderItem, Order, Customer, Product
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Customer).delete()
        db.query(Product).delete()
        db.commit()
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ── Product Tests ──────────────────────────────────────────────────────────────

def test_create_product():
    res = client.post("/api/v1/products", json={
        "product_name": "Widget A",
        "sku": "WGT-001",
        "price": "9.99",
        "quantity_in_stock": 50,
    })
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["data"]["sku"] == "WGT-001"


def test_create_product_duplicate_sku():
    payload = {"product_name": "Widget A", "sku": "WGT-DUP", "price": "9.99", "quantity_in_stock": 10}
    client.post("/api/v1/products", json=payload)
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 409
    assert res.json()["error_code"] == "DUPLICATE_SKU"


def test_get_product_not_found():
    res = client.get("/api/v1/products/999999")
    assert res.status_code == 404
    assert res.json()["error_code"] == "PRODUCT_NOT_FOUND"


def test_update_product():
    create_res = client.post("/api/v1/products", json={
        "product_name": "Widget B", "sku": "WGT-002", "price": "5.00", "quantity_in_stock": 20
    })
    pid = create_res.json()["data"]["id"]
    res = client.put(f"/api/v1/products/{pid}", json={"price": "7.50"})
    assert res.status_code == 200
    assert float(res.json()["data"]["price"]) == 7.50


def test_delete_product():
    create_res = client.post("/api/v1/products", json={
        "product_name": "Widget C", "sku": "WGT-003", "price": "3.00", "quantity_in_stock": 5
    })
    pid = create_res.json()["data"]["id"]
    res = client.delete(f"/api/v1/products/{pid}")
    assert res.status_code == 200
    assert client.get(f"/api/v1/products/{pid}").status_code == 404


# ── Customer Tests ─────────────────────────────────────────────────────────────

def test_create_customer():
    res = client.post("/api/v1/customers", json={
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "phone_number": "+1-555-0100",
    })
    assert res.status_code == 201
    assert res.json()["data"]["email"] == "alice@example.com"


def test_create_customer_duplicate_email():
    payload = {"full_name": "Bob", "email": "bob@example.com"}
    client.post("/api/v1/customers", json=payload)
    res = client.post("/api/v1/customers", json=payload)
    assert res.status_code == 409
    assert res.json()["error_code"] == "DUPLICATE_EMAIL"


# ── Order Tests ────────────────────────────────────────────────────────────────

def _seed_customer_and_product():
    c = client.post("/api/v1/customers", json={"full_name": "Test User", "email": "test@order.com"}).json()["data"]
    p = client.post("/api/v1/products", json={
        "product_name": "Item X", "sku": "ITM-X01", "price": "10.00", "quantity_in_stock": 100
    }).json()["data"]
    return c["id"], p["id"]


def test_create_order():
    cid, pid = _seed_customer_and_product()
    res = client.post("/api/v1/orders", json={
        "customer_id": cid,
        "items": [{"product_id": pid, "quantity": 3}],
    })
    assert res.status_code == 201
    data = res.json()["data"]
    assert float(data["total_amount"]) == 30.00
    # Verify stock was decremented
    stock = client.get(f"/api/v1/products/{pid}").json()["data"]["quantity_in_stock"]
    assert stock == 97


def test_order_insufficient_stock():
    cid, pid = _seed_customer_and_product()
    res = client.post("/api/v1/orders", json={
        "customer_id": cid,
        "items": [{"product_id": pid, "quantity": 9999}],
    })
    assert res.status_code == 422
    assert res.json()["error_code"] == "INSUFFICIENT_STOCK"


def test_order_invalid_customer():
    client.post("/api/v1/products", json={
        "product_name": "Item Y", "sku": "ITM-Y01", "price": "5.00", "quantity_in_stock": 10
    })
    res = client.post("/api/v1/orders", json={
        "customer_id": 999999,
        "items": [{"product_id": 1, "quantity": 1}],
    })
    assert res.status_code == 404


def test_delete_order_restores_stock():
    cid, pid = _seed_customer_and_product()
    order_res = client.post("/api/v1/orders", json={
        "customer_id": cid, "items": [{"product_id": pid, "quantity": 5}]
    })
    oid = order_res.json()["data"]["id"]
    client.delete(f"/api/v1/orders/{oid}")
    stock = client.get(f"/api/v1/products/{pid}").json()["data"]["quantity_in_stock"]
    assert stock == 100


def test_dashboard():
    res = client.get("/api/v1/dashboard")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "total_products" in data
    assert "total_customers" in data
    assert "total_orders" in data
