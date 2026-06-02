PRODUCT = {"product_name": "Gadget", "sku": "GDG-001", "price": "10.00", "quantity_in_stock": 5}
CUSTOMER = {"full_name": "Alice Smith", "email": "alice@example.com", "phone_number": None}


def _seed(client):
    p = client.post("/api/v1/products", json=PRODUCT).json()["data"]
    c = client.post("/api/v1/customers", json=CUSTOMER).json()["data"]
    return p, c


def test_create_order_success(client):
    product, customer = _seed(client)
    payload = {"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 3}]}
    res = client.post("/api/v1/orders", json=payload)
    assert res.status_code == 201
    data = res.json()["data"]
    assert float(data["total_amount"]) == 30.0

    # Verify stock decremented
    stock = client.get(f"/api/v1/products/{product['id']}").json()["data"]["quantity_in_stock"]
    assert stock == 2


def test_create_order_insufficient_stock(client):
    product, customer = _seed(client)
    payload = {"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 99}]}
    res = client.post("/api/v1/orders", json=payload)
    assert res.status_code == 422
    assert res.json()["error_code"] == "INSUFFICIENT_STOCK"


def test_create_order_customer_not_found(client):
    product, _ = _seed(client)
    payload = {"customer_id": 9999, "items": [{"product_id": product["id"], "quantity": 1}]}
    res = client.post("/api/v1/orders", json=payload)
    assert res.status_code == 404
    assert res.json()["error_code"] == "CUSTOMER_NOT_FOUND"


def test_create_order_product_not_found(client):
    _, customer = _seed(client)
    payload = {"customer_id": customer["id"], "items": [{"product_id": 9999, "quantity": 1}]}
    res = client.post("/api/v1/orders", json=payload)
    assert res.status_code == 404
    assert res.json()["error_code"] == "PRODUCT_NOT_FOUND"


def test_delete_order(client):
    product, customer = _seed(client)
    payload = {"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 1}]}
    order_id = client.post("/api/v1/orders", json=payload).json()["data"]["id"]
    assert client.delete(f"/api/v1/orders/{order_id}").status_code == 204
    assert client.get(f"/api/v1/orders/{order_id}").status_code == 404
