"""
Unit Tests – Custom Exception Classes
Verifies error codes, HTTP status codes, and messages for every exception type.
"""
import pytest

from app.core.exceptions import (
    BaseAppException,
    NotFoundError,
    DuplicateError,
    InsufficientStockError,
    ValidationError,
    DatabaseError,
)


class TestBaseAppException:
    def test_stores_all_fields(self):
        exc = BaseAppException("msg", "CODE", 418, {"k": "v"})
        assert exc.message == "msg"
        assert exc.error_code == "CODE"
        assert exc.status_code == 418
        assert exc.details == {"k": "v"}

    def test_default_status_400(self):
        exc = BaseAppException("msg", "CODE")
        assert exc.status_code == 400

    def test_default_details_empty_dict(self):
        exc = BaseAppException("msg", "CODE")
        assert exc.details == {}

    def test_is_exception(self):
        exc = BaseAppException("msg", "CODE")
        assert isinstance(exc, Exception)


class TestNotFoundError:
    def test_status_404(self):
        exc = NotFoundError("Product", 42)
        assert exc.status_code == 404

    def test_error_code_includes_resource(self):
        exc = NotFoundError("Order", 1)
        assert exc.error_code == "ORDER_NOT_FOUND"

    def test_message_includes_identifier(self):
        exc = NotFoundError("Product", 999)
        assert "999" in exc.message

    def test_details_contain_resource_and_id(self):
        exc = NotFoundError("Customer", 5)
        assert exc.details["resource"] == "Customer"
        assert exc.details["identifier"] == "5"


class TestDuplicateError:
    def test_status_409(self):
        exc = DuplicateError("Product", "SKU", "ABC-123")
        assert exc.status_code == 409

    def test_error_code_includes_field(self):
        exc = DuplicateError("Customer", "email", "x@y.com")
        assert exc.error_code == "DUPLICATE_EMAIL"

    def test_message_includes_value(self):
        exc = DuplicateError("Product", "SKU", "XYZ")
        assert "XYZ" in exc.message

    def test_details_contain_resource_field_value(self):
        exc = DuplicateError("Product", "SKU", "A1")
        assert exc.details["resource"] == "Product"
        assert exc.details["field"] == "SKU"
        assert exc.details["value"] == "A1"


class TestInsufficientStockError:
    def test_status_400(self):
        exc = InsufficientStockError(1, 10, 5)
        assert exc.status_code == 400

    def test_error_code(self):
        exc = InsufficientStockError(1, 10, 5)
        assert exc.error_code == "INSUFFICIENT_STOCK"

    def test_details_contain_quantities(self):
        exc = InsufficientStockError(7, 20, 3)
        assert exc.details["product_id"] == 7
        assert exc.details["requested_quantity"] == 20
        assert exc.details["available_quantity"] == 3

    def test_message_includes_product_id(self):
        exc = InsufficientStockError(42, 5, 2)
        assert "42" in exc.message


class TestValidationError:
    def test_status_422(self):
        exc = ValidationError("bad input")
        assert exc.status_code == 422

    def test_error_code(self):
        exc = ValidationError("bad input")
        assert exc.error_code == "VALIDATION_ERROR"

    def test_message_stored(self):
        exc = ValidationError("must be positive")
        assert exc.message == "must be positive"

    def test_optional_details(self):
        exc = ValidationError("err", {"field": "price"})
        assert exc.details["field"] == "price"

    def test_no_details_defaults_empty(self):
        exc = ValidationError("err")
        assert exc.details == {}


class TestDatabaseError:
    def test_status_500(self):
        exc = DatabaseError()
        assert exc.status_code == 500

    def test_error_code(self):
        exc = DatabaseError()
        assert exc.error_code == "DATABASE_ERROR"

    def test_default_message(self):
        exc = DatabaseError()
        assert "database" in exc.message.lower()

    def test_custom_message(self):
        exc = DatabaseError("connection refused")
        assert exc.message == "connection refused"
