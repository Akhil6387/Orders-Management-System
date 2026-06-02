from sqlalchemy.orm import Session

from app.core.exceptions import CustomerNotFoundException, DuplicateEmailException
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate


class CustomerService:

    def __init__(self, db: Session) -> None:
        self.repo = CustomerRepository(db)
        self.db = db

    def get_all(
        self, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> tuple[list[Customer], int]:
        return self.repo.get_all(skip=skip, limit=limit, search=search)

    def get_by_id(self, customer_id: int) -> Customer:
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException(customer_id)
        return customer

    def create(self, data: CustomerCreate) -> Customer:
        if self.repo.get_by_email(data.email):
            raise DuplicateEmailException(data.email)
        customer = self.repo.create(data)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer_id: int) -> None:
        customer = self.get_by_id(customer_id)
        self.repo.delete(customer)
        self.db.commit()
