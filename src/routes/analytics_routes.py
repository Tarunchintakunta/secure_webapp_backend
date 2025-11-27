from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from src.controllers.analytics_controller import (
    get_dashboard_stats,
    get_sales_report,
    get_product_analytics,
    get_low_stock_products,
    get_top_selling_products,
    get_revenue_by_date_range
)
from src.middleware.auth_middleware import get_current_user, get_current_admin
from src.models.user import UserResponse
from src.config.database import get_database

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
async def dashboard_stats(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    return await get_dashboard_stats(current_user, db)

@router.get("/sales/report")
async def sales_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    return await get_sales_report(start_date, end_date, current_user, db)

@router.get("/products")
async def product_analytics(
    current_user: UserResponse = Depends(get_current_admin),
    db=Depends(get_database)
):
    return await get_product_analytics(db)

@router.get("/products/low-stock")
async def low_stock(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    return await get_low_stock_products(db)

@router.get("/products/top-selling")
async def top_selling(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    return await get_top_selling_products(limit, db)

@router.get("/revenue")
async def revenue_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_admin),
    db=Depends(get_database)
):
    return await get_revenue_by_date_range(start_date, end_date, db)

