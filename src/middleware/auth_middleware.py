from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from src.config.settings import settings
from src.config.database import get_database
from src.models.user import UserResponse

async def get_current_user(request: Request, db=Depends(get_database)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    try:
        scheme, _, param = token.partition(" ")
        payload = jwt.decode(param, settings.JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = await db["users"].find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
        
    return UserResponse(**user)

async def get_current_admin(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin":
        # SECURITY NOTE: RBAC check
        # Insecure: Allowing any authenticated user to access admin routes
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user
