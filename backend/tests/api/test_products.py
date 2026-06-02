import pytest


PRODUCT_PAYLOAD = {
    "product_name": "Test Widget",
    "sku": "TWG-001",
    "price": "19.99",
    "quantity_in_stock": 50,
}


def test_create_product(client):
    res = client.post("/api/v1/products", json=PRODUCT_PAYLOAD)
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["sku"] == "TWG-001"
    assert data["quantity_in_stock"] == 50


def test_create_product_duplicate_sku(client):
    client.post("/api/v1/products", json=PRODUCT_PAYLOAD)
    res = client.post("/api/v1/products", json=PRODUCT_PAYLOAD)
    assert res.status_code == 409
    assert res.json()["error_code"] == "DUPLICATE_SKU"


def test_get_products(client):
    client.post("/api/v1/products", json=PRODUCT_PAYLOAD)
    res = client.get("/api/v1/products")
    assert res.status_code == 200
    assert res.json()["total"] == 1


def test_get_product_not_found(client):
    res = client.get("/api/v1/products/9999")
    assert res.status_code == 404
    assert res.json()["error_code"] == "PRODUCT_NOT_FOUND"


def test_update_product(client):
    create_res = client.post("/api/v1/products", json=PRODUCT_PAYLOAD)
    product_id = create_res.json()["data"]["id"]
    res = client.put(f"/api/v1/products/{product_id}", json={"product_name": "Updated Widget"})
    assert res.status_code == 200
    assert res.json()["data"]["product_name"] == "Updated Widget"


def test_delete_product(client):
    create_res = client.post("/api/v1/products", json=PRODUCT_PAYLOAD)
    product_id = create_res.json()["data"]["id"]
    res = client.delete(f"/api/v1/products/{product_id}")
    assert res.status_code == 204
    assert client.get(f"/api/v1/products/{product_id}").status_code == 404
