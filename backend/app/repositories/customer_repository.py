from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


class CustomerRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        stmt = select(Customer).where(Customer.email == email)
        return self.db.scalar(stmt)

    def get_all(self, skip: int = 0, limit: int = 100, search: str | None = None) -> tuple[list[Customer], int]:
        stmt = select(Customer)
        count_stmt = select(func.count()).select_from(Customer)

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                Customer.full_name.ilike(pattern) | Customer.email.ilike(pattern)
            )
            count_stmt = count_stmt.where(
                Customer.full_name.ilike(pattern) | Customer.email.ilike(pattern)
            )

        total = self.db.scalar(count_stmt) or 0
        customers = list(self.db.scalars(stmt.offset(skip).limit(limit)))
        return customers, total

    def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(**data.model_dump())
        self.db.add(customer)
        self.db.flush()
        return customer

    def delete(self, customer: Customer) -> None:
        self.db.delete(customer)
        self.db.flush()

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Customer)) or 0
