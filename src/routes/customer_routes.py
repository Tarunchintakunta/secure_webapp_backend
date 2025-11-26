from fastapi import APIRouter, Depends
from typing import List
from src.controllers.customer_controller import create_customer, get_customers, get_sales_analytics
from src.models.customer import CustomerCreate, CustomerResponse
from src.middleware.auth_middleware import get_current_admin
from src.config.database import get_database

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse, dependencies=[Depends(get_current_admin)])
async def create(customer: CustomerCreate, db=Depends(get_database)):
    return await create_customer(customer, db)

@router.get("/", response_model=List[CustomerResponse], dependencies=[Depends(get_current_admin)])
async def read_all(db=Depends(get_database)):
    return await get_customers(db)

@router.get("/analytics", dependencies=[Depends(get_current_admin)])
async def analytics(db=Depends(get_database)):
    return await get_sales_analytics(db)
