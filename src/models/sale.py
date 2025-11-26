from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from src.models.user import PyObjectId

class SaleItem(BaseModel):
    product_id: str
    quantity: int
    price_at_sale: float

class SaleCreate(BaseModel):
    items: List[SaleItem]
    customer_name: Optional[str] = None

class SaleInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    items: List[SaleItem]
    total_amount: float
    employee_id: str
    customer_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed" # completed, cancelled

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class SaleResponse(SaleInDB):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
