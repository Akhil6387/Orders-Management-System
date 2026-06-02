from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import (
    CustomerNotFoundException,
    OrderNotFoundException,
    ProductNotFoundException,
    InsufficientStockException,
    EmptyOrderException,
)
from app.models.order import Order, OrderItem
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreate


class OrderService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Order], int]:
        return self.order_repo.get_all(skip=skip, limit=limit)

    def get_by_id(self, order_id: int) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundException(order_id)
        return order

    def create(self, data: OrderCreate) -> Order:
        """
        Atomically:
          1. Validate customer exists.
          2. Validate all products exist and have sufficient stock.
          3. Decrement stock for each product.
          4. Create Order + OrderItems with backend-calculated total.
          5. Commit — or rollback on any failure.
        """
        if not data.items:
            raise EmptyOrderException()

        # 1. Validate customer
        customer = self.customer_repo.get_by_id(data.customer_id)
        if not customer:
            raise CustomerNotFoundException(data.customer_id)

        # 2. Validate products + stock (all checks before any mutation)
        resolved_items: list[tuple] = []  # (product, quantity)
        for item in data.items:
            product = self.product_repo.get_by_id(item.product_id)
            if not product:
                raise ProductNotFoundException(item.product_id)
            if product.quantity_in_stock < item.quantity:
                raise InsufficientStockException(
                    product_name=product.product_name,
                    available=product.quantity_in_stock,
                    requested=item.quantity,
                )
            resolved_items.append((product, item.quantity))

        # 3 & 4. Mutate stock and build order — all inside one transaction block
        try:
            total_amount = Decimal("0.00")
            order_items: list[OrderItem] = []

            for product, quantity in resolved_items:
                product.quantity_in_stock -= quantity
                self.db.flush()  # Enforce DB constraints immediately

                unit_price = Decimal(str(product.price))
                total_amount += unit_price * quantity
                order_items.append(
                    OrderItem(
                        product_id=product.id,
                        quantity=quantity,
                        unit_price=unit_price,
                    )
                )

            order = Order(
                customer_id=data.customer_id,
                total_amount=total_amount,
                order_items=order_items,
            )
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)

        except Exception:
            self.db.rollback()
            raise

        return self.order_repo.get_by_id(order.id)  # type: ignore[return-value]

    def delete(self, order_id: int) -> None:
        order = self.get_by_id(order_id)
        self.order_repo.delete(order)
        self.db.commit()
