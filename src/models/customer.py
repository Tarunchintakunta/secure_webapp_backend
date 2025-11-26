from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId
from src.models.user import PyObjectId

class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerInDB(CustomerBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class CustomerResponse(CustomerBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
