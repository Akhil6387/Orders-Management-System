from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderItem


class OrderRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def _eager_load(self):
        """Return a select with eager-loaded relations to avoid N+1."""
        return (
            select(Order)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product)
            )
        )

    def get_by_id(self, order_id: int) -> Order | None:
        stmt = self._eager_load().where(Order.id == order_id)
        return self.db.scalar(stmt)

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Order], int]:
        total = self.db.scalar(select(func.count()).select_from(Order)) or 0
        orders = list(
            self.db.scalars(
                self._eager_load()
                .order_by(Order.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
        )
        return orders, total

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def delete(self, order: Order) -> None:
        self.db.delete(order)
        self.db.flush()

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Order)) or 0
