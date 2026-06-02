class AppBaseException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, error_code: str, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


# --- Resource Not Found ---

class ProductNotFoundException(AppBaseException):
    def __init__(self, product_id: int):
        super().__init__(
            message=f"Product with id {product_id} not found.",
            error_code="PRODUCT_NOT_FOUND",
            status_code=404,
        )


class CustomerNotFoundException(AppBaseException):
    def __init__(self, customer_id: int):
        super().__init__(
            message=f"Customer with id {customer_id} not found.",
            error_code="CUSTOMER_NOT_FOUND",
            status_code=404,
        )


class OrderNotFoundException(AppBaseException):
    def __init__(self, order_id: int):
        super().__init__(
            message=f"Order with id {order_id} not found.",
            error_code="ORDER_NOT_FOUND",
            status_code=404,
        )


# --- Conflict / Duplicate ---

class DuplicateSKUException(AppBaseException):
    def __init__(self, sku: str):
        super().__init__(
            message=f"A product with SKU '{sku}' already exists.",
            error_code="DUPLICATE_SKU",
            status_code=409,
        )


class DuplicateEmailException(AppBaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"A customer with email '{email}' already exists.",
            error_code="DUPLICATE_EMAIL",
            status_code=409,
        )


# --- Business Rule Violations ---

class InsufficientStockException(AppBaseException):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            message=(
                f"Insufficient stock for '{product_name}'. "
                f"Available: {available}, Requested: {requested}."
            ),
            error_code="INSUFFICIENT_STOCK",
            status_code=422,
        )


class NegativeQuantityException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Product quantity cannot be negative.",
            error_code="NEGATIVE_QUANTITY",
            status_code=422,
        )


class EmptyOrderException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="An order must contain at least one item.",
            error_code="EMPTY_ORDER",
            status_code=422,
        )
