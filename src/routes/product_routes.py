from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from src.controllers.product_controller import (
    create_product, get_products, get_product, update_product, delete_product,
    search_products, get_categories
)
from src.models.product import ProductCreate, ProductUpdate, ProductResponse
from src.middleware.auth_middleware import get_current_admin, get_current_user
from src.config.database import get_database

router = APIRouter(prefix="/products", tags=["Products"])

# SECURITY NOTE: Admin only routes for modification
# Insecure: Allowing employees to create/delete products
@router.post("/", response_model=ProductResponse, dependencies=[Depends(get_current_admin)])
async def create(product: ProductCreate, db=Depends(get_database)):
    return await create_product(product, db)

@router.get("/", response_model=List[ProductResponse], dependencies=[Depends(get_current_user)])
async def read_all(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    low_stock_only: Optional[bool] = Query(False),
    db=Depends(get_database)
):
    if search or category or min_price or max_price or low_stock_only:
        return await search_products(search, category, min_price, max_price, low_stock_only, db)
    return await get_products(db)

@router.get("/categories", dependencies=[Depends(get_current_user)])
async def categories(db=Depends(get_database)):
    return await get_categories(db)

@router.get("/{id}", response_model=ProductResponse, dependencies=[Depends(get_current_user)])
async def read_one(id: str, db=Depends(get_database)):
    return await get_product(id, db)

@router.put("/{id}", response_model=ProductResponse, dependencies=[Depends(get_current_admin)])
async def update(id: str, product: ProductUpdate, db=Depends(get_database)):
    return await update_product(id, product, db)

@router.delete("/{id}", dependencies=[Depends(get_current_admin)])
async def delete(id: str, db=Depends(get_database)):
    return await delete_product(id, db)
