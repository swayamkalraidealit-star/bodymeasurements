"""Authentication utilities: password hashing and JWT token management."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Truncates password to 72 bytes to match bcrypt's limit.
    """
    # Encode to bytes and truncate to 72 bytes (bcrypt's limit)
    password_bytes = plain_password.encode('utf-8')[:72]
    # Decode back to string for passlib
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password.
    
    Bcrypt has a 72-byte limit, so we truncate to 72 bytes before hashing.
    This is a standard practice since bcrypt ignores bytes beyond 72 anyway.
    """
    # Encode to bytes and truncate to 72 bytes (bcrypt's limit)
    password_bytes = password.encode('utf-8')[:72]
    # Decode back to string for passlib
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT access token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
