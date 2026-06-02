"""
Unit Tests – OrderService
Tests business logic for order creation, status transitions, cancellation and deletion.
"""
import pytest
from decimal import Decimal

from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderItemCreate, OrderStatusUpdate
from app.models.order import OrderStatus
from app.core.exceptions import NotFoundError, InsufficientStockError, ValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _svc(db):
    return OrderService(db)


def _order_payload(customer_id: int, product_id: int, qty: int = 2) -> OrderCreate:
    return OrderCreate(
        customer_id=customer_id,
        items=[OrderItemCreate(product_id=product_id, quantity=qty)],
    )


# ---------------------------------------------------------------------------
# create_order
# ---------------------------------------------------------------------------

class TestCreateOrder:
    def test_creates_order_with_correct_total(
        self, db_session, persisted_product, persisted_customer
    ):
        svc = _svc(db_session)
        order = svc.create_order(
            _order_payload(persisted_customer.id, persisted_product.id, qty=3)
        )
        expected_total = persisted_product.price * 3
        assert order.id is not None
        assert order.total_amount == expected_total
        assert order.status == OrderStatus.PENDING

    def test_reduces_product_stock(self, db_session, persisted_product, persisted_customer):
        initial_stock = persisted_product.quantity_in_stock
        svc = _svc(db_session)
        svc.create_order(_order_payload(persisted_customer.id, persisted_product.id, qty=5))
        db_session.refresh(persisted_product)
        assert persisted_product.quantity_in_stock == initial_stock - 5

    def test_order_contains_correct_items(
        self, db_session, persisted_product, persisted_customer
    ):
        svc = _svc(db_session)
        order = svc.create_order(
            _order_payload(persisted_customer.id, persisted_product.id, qty=2)
        )
        assert len(order.order_items) == 1
        item = order.order_items[0]
        assert item.product_id == persisted_product.id
        assert item.quantity == 2
        assert item.unit_price == persisted_product.price

    def test_raises_not_found_for_missing_customer(
        self, db_session, persisted_product
    ):
        svc = _svc(db_session)
        with pytest.raises(NotFoundError) as exc_info:
            svc.create_order(_order_payload(99999, persisted_product.id))
        assert "Customer" in str(exc_info.value)

    def test_raises_not_found_for_missing_product(
        self, db_session, persisted_customer
    ):
        svc = _svc(db_session)
        with pytest.raises(NotFoundError) as exc_info:
            svc.create_order(_order_payload(persisted_customer.id, 99999))
        assert "Product" in str(exc_info.value)

    def test_raises_insufficient_stock(self, db_session, persisted_product, persisted_customer):
        svc = _svc(db_session)
        over_qty = persisted_product.quantity_in_stock + 1
        with pytest.raises(InsufficientStockError) as exc_info:
            svc.create_order(
                _order_payload(persisted_customer.id, persisted_product.id, qty=over_qty)
            )
        assert exc_info.value.status_code == 400

    def test_stock_not_changed_on_failure(
        self, db_session, persisted_product, persisted_customer
    ):
        """A failed order must not leave partial stock deductions."""
        initial_stock = persisted_product.quantity_in_stock
        svc = _svc(db_session)
        with pytest.raises((NotFoundError, InsufficientStockError)):
            svc.create_order(
                OrderCreate(
                    customer_id=persisted_customer.id,
                    items=[
                        OrderItemCreate(product_id=persisted_product.id, quantity=1),
                        OrderItemCreate(product_id=99999, quantity=1),  # bad product
                    ],
                )
            )
        db_session.refresh(persisted_product)
        assert persisted_product.quantity_in_stock == initial_stock

    def test_multi_item_order_total_correct(
        self, db_session, persisted_product, persisted_customer,
        another_product_data
    ):
        from app.models.product import Product
        p2 = Product(
            product_name=another_product_data["product_name"],
            sku=another_product_data["sku"].upper(),
            price=Decimal(str(another_product_data["price"])),
            quantity_in_stock=another_product_data["quantity_in_stock"],
        )
        db_session.add(p2)
        db_session.commit()
        db_session.refresh(p2)

        svc = _svc(db_session)
        order = svc.create_order(
            OrderCreate(
                customer_id=persisted_customer.id,
                items=[
                    OrderItemCreate(product_id=persisted_product.id, quantity=2),
                    OrderItemCreate(product_id=p2.id, quantity=3),
                ],
            )
        )
        expected = persisted_product.price * 2 + p2.price * 3
        assert order.total_amount == expected
        assert len(order.order_items) == 2


# ---------------------------------------------------------------------------
# get_order / get_orders
# ---------------------------------------------------------------------------

class TestGetOrder:
    def test_get_order_returns_correct_data(self, db_session, persisted_order):
        svc = _svc(db_session)
        order = svc.get_order(persisted_order.id)
        assert order.id == persisted_order.id

    def test_get_order_raises_not_found(self, db_session):
        svc = _svc(db_session)
        with pytest.raises(NotFoundError):
            svc.get_order(99999)

    def test_get_orders_returns_list(self, db_session, persisted_order):
        svc = _svc(db_session)
        orders, total = svc.get_orders()
        assert total >= 1
        ids = [o.id for o in orders]
        assert persisted_order.id in ids

    def test_filter_by_status(self, db_session, persisted_order):
        svc = _svc(db_session)
        orders, _ = svc.get_orders(status=OrderStatus.PENDING)
        assert all(o.status == OrderStatus.PENDING for o in orders)

    def test_filter_by_customer(self, db_session, persisted_order, persisted_customer):
        svc = _svc(db_session)
        orders, _ = svc.get_orders(customer_id=persisted_customer.id)
        assert all(o.customer_id == persisted_customer.id for o in orders)


# ---------------------------------------------------------------------------
# update_order_status
# ---------------------------------------------------------------------------

class TestUpdateOrderStatus:
    def test_advances_status(self, db_session, persisted_order):
        svc = _svc(db_session)
        updated = svc.update_order_status(
            persisted_order.id, OrderStatusUpdate(status=OrderStatus.CONFIRMED)
        )
        assert updated.status == OrderStatus.CONFIRMED

    def test_raises_not_found_for_missing_order(self, db_session):
        svc = _svc(db_session)
        with pytest.raises(NotFoundError):
            svc.update_order_status(99999, OrderStatusUpdate(status=OrderStatus.CONFIRMED))

    def test_cannot_update_cancelled_order(self, db_session, persisted_order):
        svc = _svc(db_session)
        svc.cancel_order(persisted_order.id)
        with pytest.raises(ValidationError) as exc_info:
            svc.update_order_status(
                persisted_order.id, OrderStatusUpdate(status=OrderStatus.CONFIRMED)
            )
        assert "cancel" in str(exc_info.value).lower()

    def test_cannot_move_delivered_order_backward(self, db_session, persisted_order):
        svc = _svc(db_session)
        svc.update_order_status(
            persisted_order.id, OrderStatusUpdate(status=OrderStatus.DELIVERED)
        )
        with pytest.raises(ValidationError):
            svc.update_order_status(
                persisted_order.id, OrderStatusUpdate(status=OrderStatus.PENDING)
            )


# ---------------------------------------------------------------------------
# cancel_order
# ---------------------------------------------------------------------------

class TestCancelOrder:
    def test_cancel_pending_order(self, db_session, persisted_order):
        svc = _svc(db_session)
        cancelled = svc.cancel_order(persisted_order.id)
        assert cancelled.status == OrderStatus.CANCELLED

    def test_cancel_confirmed_order(self, db_session, persisted_order):
        svc = _svc(db_session)
        svc.update_order_status(
            persisted_order.id, OrderStatusUpdate(status=OrderStatus.CONFIRMED)
        )
        cancelled = svc.cancel_order(persisted_order.id)
        assert cancelled.status == OrderStatus.CANCELLED

    def test_cancel_restores_stock(self, db_session, persisted_order, persisted_product):
        stock_before_cancel = persisted_product.quantity_in_stock
        # Stock was already reduced when the fixture created the order
        initial_stock = stock_before_cancel + 1  # 1 item ordered in fixture

        svc = _svc(db_session)
        svc.cancel_order(persisted_order.id)
        db_session.refresh(persisted_product)
        assert persisted_product.quantity_in_stock == initial_stock

    def test_cannot_cancel_shipped_order(self, db_session, persisted_order):
        svc = _svc(db_session)
        svc.update_order_status(
            persisted_order.id, OrderStatusUpdate(status=OrderStatus.SHIPPED)
        )
        with pytest.raises(ValidationError):
            svc.cancel_order(persisted_order.id)

    def test_cannot_cancel_delivered_order(self, db_session, persisted_order):
        svc = _svc(db_session)
        svc.update_order_status(
            persisted_order.id, OrderStatusUpdate(status=OrderStatus.DELIVERED)
        )
        with pytest.raises(ValidationError):
            svc.cancel_order(persisted_order.id)

    def test_raises_not_found_for_missing_order(self, db_session):
        svc = _svc(db_session)
        with pytest.raises(NotFoundError):
            svc.cancel_order(99999)


# ---------------------------------------------------------------------------
# delete_order
# ---------------------------------------------------------------------------

class TestDeleteOrder:
    def test_deletes_cancelled_order(self, db_session, persisted_order):
        svc = _svc(db_session)
        svc.cancel_order(persisted_order.id)
        result = svc.delete_order(persisted_order.id)
        assert result is True
        with pytest.raises(NotFoundError):
            svc.get_order(persisted_order.id)

    def test_raises_validation_error_for_non_cancelled(self, db_session, persisted_order):
        svc = _svc(db_session)
        with pytest.raises(ValidationError) as exc_info:
            svc.delete_order(persisted_order.id)
        assert "cancel" in str(exc_info.value).lower()

    def test_raises_not_found_for_missing_order(self, db_session):
        svc = _svc(db_session)
        with pytest.raises(NotFoundError):
            svc.delete_order(99999)
