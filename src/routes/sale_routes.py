from fastapi import APIRouter, Depends
from typing import List
from src.controllers.sale_controller import create_sale, get_sales, get_my_sales, cancel_sale
from src.models.sale import SaleCreate, SaleResponse
from src.middleware.auth_middleware import get_current_user, get_current_admin
from src.models.user import UserResponse
from src.config.database import get_database

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.post("/", response_model=SaleResponse)
async def create(sale: SaleCreate, current_user: UserResponse = Depends(get_current_user), db=Depends(get_database)):
    return await create_sale(sale, current_user.id, db)

@router.get("/", response_model=List[SaleResponse])
async def read_all(current_user: UserResponse = Depends(get_current_user), db=Depends(get_database)):
    if current_user.role == "admin":
        return await get_sales(db)
    else:
        return await get_my_sales(current_user.id, db)

@router.post("/{id}/cancel")
async def cancel(id: str, current_user: UserResponse = Depends(get_current_user), db=Depends(get_database)):
    return await cancel_sale(id, current_user.id, current_user.role, db)
