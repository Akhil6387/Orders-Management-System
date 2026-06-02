from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate,
    ProductListResponse, ProductSingleResponse,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    products, total = service.get_all(skip=skip, limit=limit, search=search)
    return {"success": True, "data": products, "total": total}


@router.get("/{product_id}", response_model=ProductSingleResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_by_id(product_id)
    return {"success": True, "data": product}


@router.post("", response_model=ProductSingleResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.create(payload)
    return {"success": True, "data": product}


@router.put("/{product_id}", response_model=ProductSingleResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.update(product_id, payload)
    return {"success": True, "data": product}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    service.delete(product_id)
