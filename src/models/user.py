from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserBase(BaseModel):
    email: EmailStr
    role: str = "employee" # admin or employee

class UserCreate(UserBase):
    password: str
    name: str

class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id")
    hashed_password: str
    name: str

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class UserResponse(UserBase):
    id: str
    name: str

    class Config:
        from_attributes = True
