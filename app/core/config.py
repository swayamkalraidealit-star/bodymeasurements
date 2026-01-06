"""Core configuration settings for the application."""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = "Body Measurement API"
    app_version: str = "1.0.0"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
