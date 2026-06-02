# Import all models here so that Alembic's autogenerate can detect them
# and so that the ORM relationship resolution works correctly.

from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order, OrderItem, OrderStatus

__all__ = ["Product", "Customer", "Order", "OrderItem", "OrderStatus"]
