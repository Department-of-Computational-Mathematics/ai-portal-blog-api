from fastapi import APIRouter
from app.api.v1.endpoints import blogs
from app.core.config import settings
api_router = APIRouter()

api_router.include_router(blogs.router, prefix=settings.SERVICE_STR) 