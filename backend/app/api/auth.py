"""Authentication endpoints."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.utils.auth import create_access_token, verify_password


router = APIRouter(prefix="/auth", tags=["authentication"])


# Schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


# Hardcoded admin credentials (for MVP)
# In production, this would be in a database
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"  # "admin123"


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    Login endpoint to get JWT access token.
    
    Args:
        login_data: Username and password
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Verify credentials
    if login_data.username != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(login_data.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": login_data.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh access token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        New JWT access token
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user["username"]},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token)


# Import at the end to avoid circular imports
from app.api.dependencies import get_current_user
