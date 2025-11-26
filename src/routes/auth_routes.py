from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from src.controllers.auth_controller import register_user, login_user, logout_user
from src.models.user import UserCreate, UserResponse
from src.middleware.auth_middleware import get_current_user
from src.config.database import get_database

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db=Depends(get_database)):
    return await register_user(user, db)

@router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_database)):
    return await login_user(response, form_data, db)

@router.post("/logout")
async def logout(response: Response):
    return await logout_user(response)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
