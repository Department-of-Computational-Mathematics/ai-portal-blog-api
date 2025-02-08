from fastapi import APIRouter
from app.api.v1.endpoints import blogs

api_router = APIRouter()

api_router.include_router(blogs.router, prefix="/blogs", tags=["blogs"]) 