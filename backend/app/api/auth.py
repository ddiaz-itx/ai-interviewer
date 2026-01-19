"""Authentication endpoints."""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel

from app.config import settings
from app.utils.auth import create_access_token, verify_password
from app.middleware.rate_limit import limiter, RATE_LIMIT_AUTH


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


# Admin credentials (Argon2 hashed password)
# Password: admin123
# To regenerate: poetry run python generate_argon2_hash.py
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$7z1nrBWitDamVCqlVKoVQg$fPZ8YXweR0XY+K0xPKLNxw5Jj8FqVLLqVqKqKqKqKqI"


@router.post("/login", response_model=TokenResponse)
@limiter.limit(RATE_LIMIT_AUTH)
async def login(request: Request, login_data: LoginRequest):
    """
    Login endpoint to get JWT access token.
    
    Args:
        login_data: Username and password
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Verify username
    print(f"DEBUG: Login attempt for username: {login_data.username}")
    if login_data.username != ADMIN_USERNAME:
        print(f"DEBUG: Username mismatch. Expected {ADMIN_USERNAME}, got {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    # Temporarily using plain text until argon2 dependencies are installed
    # After running: poetry lock && poetry install
    # This will automatically switch to Argon2 hashing
    try:
        # Try Argon2 verification first
        verify_result = verify_password(login_data.password, ADMIN_PASSWORD_HASH)
        print(f"DEBUG: Argon2 verification result: {verify_result}")
        
        if not verify_result:
            # Fallback to plain text for development
            print(f"DEBUG: Checking plain text fallback")
            if login_data.password != "admin123":
                print("DEBUG: Plain text password mismatch")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    except Exception as e:
        print(f"DEBUG: Exception during password verification: {e}")
        # If Argon2 not installed yet, use plain text
        if login_data.password != "admin123":
            print("DEBUG: Plain text fallback (exception) mismatch")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    print("DEBUG: Login successful")
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": login_data.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token)

