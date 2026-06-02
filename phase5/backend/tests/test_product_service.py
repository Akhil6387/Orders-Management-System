"""
Unit Tests – ProductService
Tests business logic in isolation using the ORM-level fixtures from conftest.
"""
import pytest
from decimal import Decimal

from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.exceptions import NotFoundError, DuplicateError, ValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service(db):
    return ProductService(db)


def _create(db, **kwargs):
    defaults = dict(
        product_name="Test Item",
        sku="TEST-UNIT-01",
        price=Decimal("10.00"),
        quantity_in_stock=50,
    )
    defaults.update(kwargs)
    svc = _make_service(db)
    return svc.create_product(ProductCreate(**defaults))


# ---------------------------------------------------------------------------
# create_product
# ---------------------------------------------------------------------------

class TestCreateProduct:
    def test_creates_with_correct_fields(self, db_session):
        svc = _make_service(db_session)
        data = ProductCreate(
            product_name="  Widget  ",
            sku="wgt-001",
            price=Decimal("19.99"),
            quantity_in_stock=100,
        )
        product = svc.create_product(data)

        assert product.id is not None
        assert product.product_name == "Widget"
        assert product.sku == "WGT-001"          # normalized to upper
        assert product.price == Decimal("19.99")
        assert product.quantity_in_stock == 100

    def test_sku_normalised_to_uppercase(self, db_session):
        product = _create(db_session, sku="abc-123")
        assert product.sku == "ABC-123"

    def test_raises_on_duplicate_sku(self, db_session):
        _create(db_session, sku="DUP-001")
        with pytest.raises(DuplicateError) as exc_info:
            _create(db_session, sku="DUP-001", product_name="Other")
        assert "DUP-001" in str(exc_info.value)

    def test_raises_on_duplicate_sku_case_insensitive(self, db_session):
        _create(db_session, sku="dup-001")
        with pytest.raises(DuplicateError):
            _create(db_session, sku="DUP-001", product_name="Other")

    def test_allows_zero_price(self, db_session):
        product = _create(db_session, price=Decimal("0.00"))
        assert product.price == Decimal("0.00")

    def test_allows_zero_stock(self, db_session):
        product = _create(db_session, quantity_in_stock=0)
        assert product.quantity_in_stock == 0


# ---------------------------------------------------------------------------
# get_product
# ---------------------------------------------------------------------------

class TestGetProduct:
    def test_returns_existing_product(self, db_session, persisted_product):
        svc = _make_service(db_session)
        result = svc.get_product(persisted_product.id)
        assert result.id == persisted_product.id
        assert result.sku == persisted_product.sku

    def test_raises_not_found_for_missing_id(self, db_session):
        svc = _make_service(db_session)
        with pytest.raises(NotFoundError):
            svc.get_product(99999)


# ---------------------------------------------------------------------------
# get_products
# ---------------------------------------------------------------------------

class TestGetProducts:
    def test_returns_empty_list_when_no_products(self, db_session):
        svc = _make_service(db_session)
        products, total = svc.get_products()
        assert products == []
        assert total == 0

    def test_returns_all_products_with_correct_total(self, db_session):
        _create(db_session, sku="P-001")
        _create(db_session, sku="P-002", product_name="Another")
        svc = _make_service(db_session)
        products, total = svc.get_products(page=1, page_size=10)
        assert total == 2
        assert len(products) == 2

    def test_pagination_works(self, db_session):
        for i in range(5):
            _create(db_session, sku=f"PAG-{i:03d}", product_name=f"Product {i}")
        svc = _make_service(db_session)
        first_page, total = svc.get_products(page=1, page_size=2)
        assert len(first_page) == 2
        assert total == 5

    def test_search_filters_by_name(self, db_session):
        _create(db_session, sku="S-001", product_name="Alpha Widget")
        _create(db_session, sku="S-002", product_name="Beta Gadget")
        svc = _make_service(db_session)
        results, total = svc.get_products(search="Widget")
        assert total == 1
        assert results[0].product_name == "Alpha Widget"

    def test_search_filters_by_sku(self, db_session):
        _create(db_session, sku="FIND-ME", product_name="Generic")
        _create(db_session, sku="OTHER-1", product_name="Other")
        svc = _make_service(db_session)
        results, total = svc.get_products(search="FIND")
        assert total == 1

    def test_search_is_case_insensitive(self, db_session):
        _create(db_session, sku="CASE-001", product_name="CaseSensitive")
        svc = _make_service(db_session)
        results, _ = svc.get_products(search="casesensitive")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# update_product
# ---------------------------------------------------------------------------

class TestUpdateProduct:
    def test_updates_name(self, db_session, persisted_product):
        svc = _make_service(db_session)
        updated = svc.update_product(persisted_product.id, ProductUpdate(product_name="New Name"))
        assert updated.product_name == "New Name"

    def test_updates_price(self, db_session, persisted_product):
        svc = _make_service(db_session)
        updated = svc.update_product(persisted_product.id, ProductUpdate(price=Decimal("99.99")))
        assert updated.price == Decimal("99.99")

    def test_updates_stock(self, db_session, persisted_product):
        svc = _make_service(db_session)
        updated = svc.update_product(persisted_product.id, ProductUpdate(quantity_in_stock=200))
        assert updated.quantity_in_stock == 200

    def test_updates_sku_and_normalizes(self, db_session, persisted_product):
        svc = _make_service(db_session)
        updated = svc.update_product(persisted_product.id, ProductUpdate(sku="new-sku"))
        assert updated.sku == "NEW-SKU"

    def test_raises_not_found_for_missing_product(self, db_session):
        svc = _make_service(db_session)
        with pytest.raises(NotFoundError):
            svc.update_product(99999, ProductUpdate(product_name="x"))

    def test_raises_duplicate_when_sku_taken(self, db_session, persisted_product):
        other = _create(db_session, sku="OTHER-SKU", product_name="Other")
        svc = _make_service(db_session)
        with pytest.raises(DuplicateError):
            svc.update_product(persisted_product.id, ProductUpdate(sku=other.sku))

    def test_same_sku_update_does_not_raise(self, db_session, persisted_product):
        """Updating a product without changing its SKU should be allowed."""
        svc = _make_service(db_session)
        updated = svc.update_product(
            persisted_product.id,
            ProductUpdate(sku=persisted_product.sku, product_name="Renamed"),
        )
        assert updated.sku == persisted_product.sku


# ---------------------------------------------------------------------------
# delete_product
# ---------------------------------------------------------------------------

class TestDeleteProduct:
    def test_deletes_product_without_orders(self, db_session, persisted_product):
        svc = _make_service(db_session)
        result = svc.delete_product(persisted_product.id)
        assert result is True
        with pytest.raises(NotFoundError):
            svc.get_product(persisted_product.id)

    def test_raises_not_found_for_missing_product(self, db_session):
        svc = _make_service(db_session)
        with pytest.raises(NotFoundError):
            svc.delete_product(99999)

    def test_raises_validation_error_when_product_has_orders(
        self, db_session, persisted_order, persisted_product
    ):
        svc = _make_service(db_session)
        with pytest.raises(ValidationError) as exc_info:
            svc.delete_product(persisted_product.id)
        assert "ordered" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# get_low_stock_products
# ---------------------------------------------------------------------------

class TestGetLowStockProducts:
    def test_returns_products_below_threshold(self, db_session):
        _create(db_session, sku="L-001", quantity_in_stock=3)
        _create(db_session, sku="L-002", quantity_in_stock=50)
        svc = _make_service(db_session)
        results = svc.get_low_stock_products(threshold=10)
        assert len(results) == 1
        assert results[0].sku == "L-001"

    def test_includes_products_at_threshold(self, db_session):
        _create(db_session, sku="AT-001", quantity_in_stock=10)
        svc = _make_service(db_session)
        results = svc.get_low_stock_products(threshold=10)
        assert len(results) == 1

    def test_returns_empty_when_all_stocked(self, db_session):
        _create(db_session, sku="OK-001", quantity_in_stock=100)
        svc = _make_service(db_session)
        results = svc.get_low_stock_products(threshold=5)
        assert results == []
