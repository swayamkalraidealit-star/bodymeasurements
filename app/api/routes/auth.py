"""Authentication routes for user registration, login, and management."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.core.auth import verify_password, get_password_hash, create_access_token
from app.core.database import get_users_collection
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.models import User, UserCreate, user_helper
from bson import ObjectId

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str  # Can be username or email
    password: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    user: User


class RegisterRequest(BaseModel):
    """Registration request model."""
    email: EmailStr
    username: str
    password: str
    confirm_password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username is alphanumeric."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate passwords match."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < settings.password_min_length:
            raise ValueError(f'Password must be at least {settings.password_min_length} characters')
        # Bcrypt has a 72-byte limit
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (maximum 72 bytes in UTF-8 encoding)')
        return v


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user."""
    
    users_collection = get_users_collection()
    
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": request.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_user = await users_collection.find_one({"username": request.username.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user document
    user_doc = {
        "email": request.email.lower(),
        "username": request.username.lower(),
        "hashed_password": get_password_hash(request.password),
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    
    # Insert user
    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Return user (without password)
    return User(**user_helper(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user and return access token."""
    
    users_collection = get_users_collection()
    
    # Find user by username or email
    user_doc = await users_collection.find_one({
        "$or": [
            {"username": request.username.lower()},
            {"email": request.username.lower()}
        ]
    })
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(request.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user_doc["_id"]), "email": user_doc["email"]}
    )
    
    # Return token and user info
    return TokenResponse(
        access_token=access_token,
        user=User(**user_helper(user_doc))
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should remove token)."""
    # In a production app, you might maintain a token blacklist
    # For now, we rely on client-side token removal
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Verify if token is valid."""
    return {"valid": True, "user_id": current_user.id}
