from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Blog API"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
    ]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./blog.db"  # Update this based on your database configuration
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb+srv://AIPortalBlogAdmin:3F45Tohxct3jb2Ih@email.vm8njwj.mongodb.net/"
    MONGODB_DB_NAME: str = "AIPortalBlog"
    
    class Config:
        case_sensitive = True

settings = Settings() 