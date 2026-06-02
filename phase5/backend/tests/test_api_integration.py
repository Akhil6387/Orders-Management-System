"""
Integration Tests – Full API via TestClient
Covers every HTTP endpoint end-to-end through the FastAPI app with a real SQLite DB.
"""
import pytest


# ===========================================================================
# Product API
# ===========================================================================

class TestProductAPICreate:
    def test_201_valid_product(self, client, sample_product):
        r = client.post("/api/products", json=sample_product)
        assert r.status_code == 201
        body = r.json()
        assert body["success"] is True
        assert body["data"]["product_name"] == sample_product["product_name"]
        assert body["data"]["sku"] == sample_product["sku"].upper()

    def test_409_duplicate_sku(self, client, sample_product):
        client.post("/api/products", json=sample_product)
        r = client.post("/api/products", json=sample_product)
        assert r.status_code == 409
        assert "DUPLICATE" in r.json()["error_code"]

    def test_422_missing_required_fields(self, client):
        r = client.post("/api/products", json={"product_name": "Incomplete"})
        assert r.status_code == 422

    def test_422_negative_price(self, client):
        r = client.post(
            "/api/products",
            json={"product_name": "Bad", "sku": "BAD-001", "price": -1, "quantity_in_stock": 0},
        )
        assert r.status_code == 422

    def test_422_negative_stock(self, client):
        r = client.post(
            "/api/products",
            json={"product_name": "Bad", "sku": "BAD-002", "price": 1, "quantity_in_stock": -1},
        )
        assert r.status_code == 422


class TestProductAPIRead:
    def test_200_list_empty(self, client):
        r = client.get("/api/products")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["data"] == []
        assert body["pagination"]["total_items"] == 0

    def test_200_list_with_products(self, client, sample_product):
        client.post("/api/products", json=sample_product)
        r = client.get("/api/products")
        assert r.json()["pagination"]["total_items"] == 1

    def test_200_get_by_id(self, client, sample_product):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        r = client.get(f"/api/products/{pid}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == pid

    def test_404_unknown_id(self, client):
        r = client.get("/api/products/999999")
        assert r.status_code == 404
        assert "NOT_FOUND" in r.json()["error_code"]

    def test_search_returns_matching_products(self, client, sample_product):
        client.post("/api/products", json=sample_product)
        r = client.get("/api/products?search=Widget")
        assert r.json()["pagination"]["total_items"] >= 1

    def test_pagination_page_and_page_size(self, client):
        for i in range(5):
            client.post(
                "/api/products",
                json={"product_name": f"P{i}", "sku": f"PGTEST-{i}", "price": 1, "quantity_in_stock": 0},
            )
        r = client.get("/api/products?page=1&page_size=2")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2
        assert r.json()["pagination"]["total_items"] == 5

    def test_low_stock_endpoint(self, client):
        client.post(
            "/api/products",
            json={"product_name": "Scarce", "sku": "SCARCE-1", "price": 5, "quantity_in_stock": 3},
        )
        r = client.get("/api/products/low-stock?threshold=10")
        assert r.status_code == 200
        skus = [p["sku"] for p in r.json()["data"]]
        assert "SCARCE-1" in skus


class TestProductAPIUpdate:
    def test_200_update_name(self, client, sample_product):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        r = client.put(f"/api/products/{pid}", json={"product_name": "Renamed"})
        assert r.status_code == 200
        assert r.json()["data"]["product_name"] == "Renamed"

    def test_200_update_price(self, client, sample_product):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        r = client.put(f"/api/products/{pid}", json={"price": 99.99})
        assert float(r.json()["data"]["price"]) == 99.99

    def test_404_update_unknown(self, client):
        r = client.put("/api/products/999999", json={"product_name": "x"})
        assert r.status_code == 404

    def test_409_update_to_duplicate_sku(self, client, sample_product, another_product_data):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        client.post("/api/products", json=another_product_data)
        r = client.put(f"/api/products/{pid}", json={"sku": another_product_data["sku"]})
        assert r.status_code == 409


class TestProductAPIDelete:
    def test_200_delete_product(self, client, sample_product):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        r = client.delete(f"/api/products/{pid}")
        assert r.status_code == 200
        assert client.get(f"/api/products/{pid}").status_code == 404

    def test_404_delete_unknown(self, client):
        r = client.delete("/api/products/999999")
        assert r.status_code == 404


# ===========================================================================
# Customer API
# ===========================================================================

class TestCustomerAPICreate:
    def test_201_valid_customer(self, client, sample_customer):
        r = client.post("/api/customers", json=sample_customer)
        assert r.status_code == 201
        body = r.json()
        assert body["success"] is True
        assert body["data"]["email"] == sample_customer["email"].lower()

    def test_409_duplicate_email(self, client, sample_customer):
        client.post("/api/customers", json=sample_customer)
        r = client.post("/api/customers", json=sample_customer)
        assert r.status_code == 409

    def test_422_invalid_email_format(self, client):
        r = client.post(
            "/api/customers",
            json={"full_name": "Bad", "email": "not-an-email"},
        )
        assert r.status_code == 422

    def test_422_missing_name(self, client):
        r = client.post("/api/customers", json={"email": "ok@x.com"})
        assert r.status_code == 422


class TestCustomerAPIRead:
    def test_200_list(self, client, sample_customer):
        client.post("/api/customers", json=sample_customer)
        r = client.get("/api/customers")
        assert r.status_code == 200
        assert r.json()["pagination"]["total_items"] >= 1

    def test_200_get_by_id(self, client, sample_customer):
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        r = client.get(f"/api/customers/{cid}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == cid

    def test_404_unknown_id(self, client):
        r = client.get("/api/customers/999999")
        assert r.status_code == 404


class TestCustomerAPIUpdate:
    def test_200_update_name(self, client, sample_customer):
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        r = client.put(f"/api/customers/{cid}", json={"full_name": "Updated Name"})
        assert r.status_code == 200
        assert r.json()["data"]["full_name"] == "Updated Name"

    def test_404_update_unknown(self, client):
        r = client.put("/api/customers/999999", json={"full_name": "x"})
        assert r.status_code == 404


class TestCustomerAPIDelete:
    def test_200_delete(self, client, sample_customer):
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        r = client.delete(f"/api/customers/{cid}")
        assert r.status_code == 200
        assert client.get(f"/api/customers/{cid}").status_code == 404

    def test_422_delete_with_orders(self, client, sample_product, sample_customer):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": pid, "quantity": 1}]},
        )
        r = client.delete(f"/api/customers/{cid}")
        assert r.status_code in (409, 422)


# ===========================================================================
# Order API
# ===========================================================================

class TestOrderAPICreate:
    def _setup(self, client, sample_product, sample_customer):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        return pid, cid

    def test_201_basic_order(self, client, sample_product, sample_customer):
        pid, cid = self._setup(client, sample_product, sample_customer)
        r = client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": pid, "quantity": 2}]},
        )
        assert r.status_code == 201
        body = r.json()
        assert body["success"] is True
        assert float(body["data"]["total_amount"]) == round(sample_product["price"] * 2, 2)

    def test_201_order_reduces_stock(self, client, sample_product, sample_customer):
        pid, cid = self._setup(client, sample_product, sample_customer)
        initial = sample_product["quantity_in_stock"]
        client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": pid, "quantity": 5}]},
        )
        remaining = client.get(f"/api/products/{pid}").json()["data"]["quantity_in_stock"]
        assert remaining == initial - 5

    def test_400_insufficient_stock(self, client, sample_product, sample_customer):
        pid, cid = self._setup(client, sample_product, sample_customer)
        r = client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": pid, "quantity": 9999}]},
        )
        assert r.status_code == 400
        assert r.json()["error_code"] == "INSUFFICIENT_STOCK"

    def test_404_unknown_customer(self, client, sample_product):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        r = client.post(
            "/api/orders",
            json={"customer_id": 99999, "items": [{"product_id": pid, "quantity": 1}]},
        )
        assert r.status_code == 404

    def test_404_unknown_product(self, client, sample_customer):
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        r = client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": 99999, "quantity": 1}]},
        )
        assert r.status_code == 404

    def test_422_empty_items(self, client, sample_customer):
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        r = client.post("/api/orders", json={"customer_id": cid, "items": []})
        assert r.status_code == 422

    def test_422_duplicate_product_in_items(self, client, sample_product, sample_customer):
        pid, cid = self._setup(client, sample_product, sample_customer)
        r = client.post(
            "/api/orders",
            json={
                "customer_id": cid,
                "items": [
                    {"product_id": pid, "quantity": 1},
                    {"product_id": pid, "quantity": 1},
                ],
            },
        )
        assert r.status_code == 422


class TestOrderAPIRead:
    def _place_order(self, client, sample_product, sample_customer):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        oid = client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": pid, "quantity": 1}]},
        ).json()["data"]["id"]
        return oid, pid, cid

    def test_200_list_orders(self, client, sample_product, sample_customer):
        self._place_order(client, sample_product, sample_customer)
        r = client.get("/api/orders")
        assert r.status_code == 200
        assert r.json()["pagination"]["total_items"] >= 1

    def test_200_get_order_by_id(self, client, sample_product, sample_customer):
        oid, _, _ = self._place_order(client, sample_product, sample_customer)
        r = client.get(f"/api/orders/{oid}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == oid

    def test_404_unknown_order(self, client):
        r = client.get("/api/orders/999999")
        assert r.status_code == 404

    def test_filter_by_status(self, client, sample_product, sample_customer):
        self._place_order(client, sample_product, sample_customer)
        r = client.get("/api/orders?status=pending")
        assert r.status_code == 200
        data = r.json()["data"]
        assert all(o["status"] == "pending" for o in data)


class TestOrderAPIStatusUpdate:
    def _place(self, client, sample_product, sample_customer):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        return client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": pid, "quantity": 1}]},
        ).json()["data"]["id"]

    def test_200_advance_to_confirmed(self, client, sample_product, sample_customer):
        oid = self._place(client, sample_product, sample_customer)
        r = client.patch(f"/api/orders/{oid}/status", json={"status": "confirmed"})
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "confirmed"

    def test_422_update_cancelled_order(self, client, sample_product, sample_customer):
        oid = self._place(client, sample_product, sample_customer)
        client.post(f"/api/orders/{oid}/cancel")
        r = client.patch(f"/api/orders/{oid}/status", json={"status": "confirmed"})
        assert r.status_code in (422, 400)


class TestOrderAPICancel:
    def _place(self, client, sample_product, sample_customer):
        pid = client.post("/api/products", json=sample_product).json()["data"]["id"]
        cid = client.post("/api/customers", json=sample_customer).json()["data"]["id"]
        initial_stock = sample_product["quantity_in_stock"]
        oid = client.post(
            "/api/orders",
            json={"customer_id": cid, "items": [{"product_id": pid, "quantity": 10}]},
        ).json()["data"]["id"]
        return oid, pid, initial_stock

    def test_200_cancel_pending_order(self, client, sample_product, sample_customer):
        oid, _, _ = self._place(client, sample_product, sample_customer)
        r = client.post(f"/api/orders/{oid}/cancel")
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "cancelled"

    def test_cancel_restores_stock(self, client, sample_product, sample_customer):
        oid, pid, initial_stock = self._place(client, sample_product, sample_customer)
        client.post(f"/api/orders/{oid}/cancel")
        remaining = client.get(f"/api/products/{pid}").json()["data"]["quantity_in_stock"]
        assert remaining == initial_stock

    def test_422_cancel_shipped_order(self, client, sample_product, sample_customer):
        oid, _, _ = self._place(client, sample_product, sample_customer)
        client.patch(f"/api/orders/{oid}/status", json={"status": "shipped"})
        r = client.post(f"/api/orders/{oid}/cancel")
        assert r.status_code in (400, 422)


# ===========================================================================
# Dashboard API
# ===========================================================================

class TestDashboardAPI:
    def test_200_dashboard_stats(self, client):
        r = client.get("/api/dashboard")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        data = body["data"]
        # All numeric fields present
        for key in ("total_products", "total_customers", "total_orders", "total_revenue"):
            assert key in data, f"Missing key: {key}"

    def test_dashboard_reflects_created_entities(self, client, sample_product, sample_customer):
        client.post("/api/products", json=sample_product)
        client.post("/api/customers", json=sample_customer)
        r = client.get("/api/dashboard")
        data = r.json()["data"]
        assert data["total_products"] >= 1
        assert data["total_customers"] >= 1


# ===========================================================================
# Health Check
# ===========================================================================

class TestHealthCheck:
    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200
