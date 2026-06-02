from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.customer import (
    CustomerCreate, CustomerListResponse, CustomerSingleResponse,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    customers, total = service.get_all(skip=skip, limit=limit, search=search)
    return {"success": True, "data": customers, "total": total}


@router.get("/{customer_id}", response_model=CustomerSingleResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    service = CustomerService(db)
    customer = service.get_by_id(customer_id)
    return {"success": True, "data": customer}


@router.post("", response_model=CustomerSingleResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    customer = service.create(payload)
    return {"success": True, "data": customer}


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    service = CustomerService(db)
    service.delete(customer_id)
