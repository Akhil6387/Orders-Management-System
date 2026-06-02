from fastapi import APIRouter

from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.customers import router as customers_router
from app.api.v1.endpoints.orders import router as orders_router
from app.api.v1.endpoints.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(products_router)
api_router.include_router(customers_router)
api_router.include_router(orders_router)
api_router.include_router(dashboard_router)
