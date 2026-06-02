from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository


class DashboardService:

    def __init__(self, db: Session) -> None:
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.order_repo = OrderRepository(db)

    def get_stats(self) -> dict:
        _, total_products = self.product_repo.get_all(limit=0)
        total_customers = self.customer_repo.count()
        total_orders = self.order_repo.count()
        low_stock = self.product_repo.get_low_stock(threshold=10)

        return {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "low_stock_products": low_stock,
        }
