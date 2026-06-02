from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku)
        return self.db.scalar(stmt)

    def get_all(self, skip: int = 0, limit: int = 100, search: str | None = None) -> tuple[list[Product], int]:
        stmt = select(Product)
        count_stmt = select(func.count()).select_from(Product)

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                Product.product_name.ilike(pattern) | Product.sku.ilike(pattern)
            )
            count_stmt = count_stmt.where(
                Product.product_name.ilike(pattern) | Product.sku.ilike(pattern)
            )

        total = self.db.scalar(count_stmt) or 0
        products = list(self.db.scalars(stmt.offset(skip).limit(limit)))
        return products, total

    def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.db.add(product)
        self.db.flush()   # Get id without committing
        return product

    def update(self, product: Product, data: ProductUpdate) -> Product:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.flush()
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.flush()

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        stmt = select(Product).where(Product.quantity_in_stock <= threshold).order_by(Product.quantity_in_stock)
        return list(self.db.scalars(stmt))
