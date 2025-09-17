from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SERVICE_STR: str = "/blogs"
    PROJECT_NAME: str = "Blog API"
    BACKEND_CORS_ORIGINS: List[str] = [
        "*",
        "http://localhost:3000",
        "https://localhost:3000",
    ]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./blog.db"  # Update this based on your database configuration
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("BLOG_MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("BLOG_MONGODB_DB_NAME", "")

    # Keycloak settings
    KEYCLOAK_URL: str = "http://localhost:8080"
    REALM: str = "master"
    CLIENT_ID: str = "blogs-service"  # Custom client used for blog service (separation of concerns)
    CLIENT_SECRET: str = os.getenv("BLOG_CLIENT_SECRET", "")

    class Config:
        case_sensitive = True

settings = Settings() 