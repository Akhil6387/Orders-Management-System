from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product import ProductResponse
from app.services.dashboard_service import DashboardService
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    low_stock_products: list[ProductResponse]


class DashboardResponse(BaseModel):
    success: bool = True
    data: DashboardStats


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    service = DashboardService(db)
    stats = service.get_stats()
    return {"success": True, "data": stats}
