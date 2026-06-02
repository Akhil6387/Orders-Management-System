from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


# Use Annotated to apply constraints directly to the Decimal type
# so Pydantic v2 can parse it correctly even when used in Union/Optional types.
ConstrainedDecimal = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255, examples=["Widget A"])
    sku: str = Field(..., min_length=1, max_length=100, examples=["WGT-001"])
    price: ConstrainedDecimal = Field(..., examples=[9.99])
    quantity_in_stock: int = Field(default=0, ge=0, examples=[100])


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: str | None = Field(None, min_length=1, max_length=255)
    sku: str | None = Field(None, min_length=1, max_length=100)
    price: ConstrainedDecimal | None = None
    quantity_in_stock: int | None = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    success: bool = True
    data: list[ProductResponse]
    total: int


class ProductSingleResponse(BaseModel):
    success: bool = True
    data: ProductResponse
