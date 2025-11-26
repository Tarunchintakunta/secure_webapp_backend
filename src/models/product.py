from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from src.models.user import PyObjectId

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    stock_quantity: int = 0
    low_stock_threshold: int = 5

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None

class ProductInDB(ProductBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ProductResponse(ProductBase):
    id: str

    class Config:
        from_attributes = True
