from fastapi import HTTPException, status, Response, Depends
from src.models.user import UserCreate, UserInDB, UserResponse
from src.utils.auth import get_password_hash, verify_password, create_access_token
from src.config.database import get_database
from datetime import timedelta

async def register_user(user: UserCreate, db=Depends(get_database)):
    # Check if user exists
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    
    # Create user document for database
    user_doc = {
        "email": user.email,
        "role": user.role,
        "name": user.name,
        "hashed_password": hashed_password
    }
    
    new_user = await db["users"].insert_one(user_doc)
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})
    
    return UserResponse(
        id=str(created_user["_id"]),
        email=created_user["email"],
        role=created_user["role"],
        name=created_user["name"]
    )

async def login_user(response: Response, form_data, db=Depends(get_database)):
    user = await db["users"].find_one({"email": form_data.username}) # OAuth2PasswordRequestForm uses username
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        # SECURITY NOTE: Don't reveal if it's email or password that is wrong
        # Insecure: "User not found" or "Wrong password"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    # SECURITY NOTE: HttpOnly prevents XSS from reading the token
    # Insecure: localStorage or document.cookie without HttpOnly
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax", # Relaxed for localhost
        secure=False, # Set to True in production with HTTPS
        max_age=1800
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
