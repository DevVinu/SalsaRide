import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartFlow - Intelligent Traffic Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "smartflow-super-secret-jwt-key-2026-traffic-ai")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # MongoDB (defaults to False for fast standalone development, True when live MongoDB daemon is running)
    ENABLE_MONGO: bool = os.getenv("ENABLE_MONGO", "false").lower() in ("true", "1")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "smartflow_traffic_db")
    
    # Geofence & Detection Zones (Meters)
    DEFAULT_DETECTION_RADIUS_METERS: int = 500
    INNER_ZONE_RADIUS_METERS: int = 150
    MID_ZONE_RADIUS_METERS: int = 300
    
    # Virtual Signal Limits (Seconds)
    MIN_GREEN_DURATION: int = 10
    MAX_GREEN_DURATION: int = 55
    YELLOW_DURATION: int = 4
    ALL_RED_DURATION: int = 2
    STARVATION_THRESHOLD_SECONDS: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()
