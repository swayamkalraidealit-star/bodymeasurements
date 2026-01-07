"""Database models for user authentication and measurements."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ],
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str
    is_active: bool = True


class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    username: str
    password: str


class UserInDB(UserBase):
    """User model as stored in database."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(UserBase):
    """User response model (without password)."""
    id: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class UserMeasurementDB(BaseModel):
    """User measurement stored in database."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    measurements: Dict[str, Any]
    gender: str
    height: float
    units: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


def user_helper(user: dict) -> dict:
    """Convert MongoDB user document to User model."""
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
    }


def user_in_db_helper(user: dict) -> dict:
    """Convert MongoDB user document to UserInDB model."""
    return {
        "_id": user["_id"],
        "email": user["email"],
        "username": user["username"],
        "hashed_password": user["hashed_password"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
    }
