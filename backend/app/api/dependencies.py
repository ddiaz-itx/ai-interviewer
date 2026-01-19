"""Authentication dependencies for FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.auth import verify_token


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    print(f"DEBUG: Received token: {token[:10]}...")
    payload = verify_token(token)
    print(f"DEBUG: Token verification payload: {payload}")
    
    if payload is None:
        print("DEBUG: Token verification failed (payload is None)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if username is None:
        print("DEBUG: Username not found in payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username}


# Dependency for protecting admin routes
async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin authentication.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user is not admin
    """
    # For now, all authenticated users are admins
    # In production, you would check user.role == "admin"
    return current_user
