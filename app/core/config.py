"""Core configuration settings for the application."""
import os
from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = "Body Measurement API"
    app_version: str = "1.0.0"
    
    # CORS
    cors_origins: Union[str, List[str]] = "http://localhost:8000,http://127.0.0.1:8000"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Upload Settings
    upload_max_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png"]
    
    # MediaPipe Settings
    mediapipe_model_complexity: int = 1  # 0=lite, 1=full, 2=heavy
    mediapipe_min_detection_confidence: float = 0.5
    mediapipe_min_tracking_confidence: float = 0.5
    
    # Measurement Settings
    default_units: str = "metric"  # metric or imperial
    
    # Avatar Settings
    avatar_storage_dir: str = "uploads/avatars"
    avatar_assets_dir: str = "static/avatar_assets"
    clothing_assets_dir: str = "static/clothing_assets"
    default_skin_tone: str = "medium"
    avatar_image_width: int = 800
    avatar_image_height: int = 1200
    
    # Fit Simulation Settings
    fit_tolerance_perfect: float = 0.02  # 2%
    fit_tolerance_good: float = 0.05  # 5%
    length_tolerance_perfect: float = 2.0  # 2cm
    length_tolerance_acceptable: float = 5.0  # 5cm
    
    # Database Settings (MongoDB)
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "body_measurements"
    
    @field_validator('mongodb_url', mode='before')
    @classmethod
    def handle_mongodb_uri_alias(cls, v, info):
        """Support both mongodb_url and mongodb_uri environment variables."""
        # If mongodb_url is not set, try to get mongodb_uri from environment
        if v == "mongodb://localhost:27017":
            import os
            mongodb_uri = os.getenv('MONGODB_URI') or os.getenv('mongodb_uri')
            if mongodb_uri:
                return mongodb_uri
        return v
    
    # Authentication Settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_days: int = 7
    password_min_length: int = 8
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
