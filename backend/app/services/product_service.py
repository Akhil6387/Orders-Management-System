from sqlalchemy.orm import Session

from app.core.exceptions import (
    ProductNotFoundException,
    DuplicateSKUException,
    NegativeQuantityException,
)
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    def __init__(self, db: Session) -> None:
        self.repo = ProductRepository(db)
        self.db = db

    def get_all(
        self, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> tuple[list[Product], int]:
        return self.repo.get_all(skip=skip, limit=limit, search=search)

    def get_by_id(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        return product

    def create(self, data: ProductCreate) -> Product:
        if data.quantity_in_stock < 0:
            raise NegativeQuantityException()
        if self.repo.get_by_sku(data.sku):
            raise DuplicateSKUException(data.sku)
        product = self.repo.create(data)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get_by_id(product_id)

        if data.quantity_in_stock is not None and data.quantity_in_stock < 0:
            raise NegativeQuantityException()

        if data.sku and data.sku != product.sku:
            if self.repo.get_by_sku(data.sku):
                raise DuplicateSKUException(data.sku)

        updated = self.repo.update(product, data)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        self.repo.delete(product)
        self.db.commit()

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        return self.repo.get_low_stock(threshold)
