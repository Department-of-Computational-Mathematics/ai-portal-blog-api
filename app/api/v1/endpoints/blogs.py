from typing import List
from fastapi import APIRouter, HTTPException
from app import schemas, services

router = APIRouter()

@router.get("/", response_model=List[schemas.Blog])
async def get_blogs(skip: int = 0, limit: int = 100):
    blogs = await services.blog.get_blogs(skip=skip, limit=limit)
    return blogs

@router.post("/", response_model=schemas.Blog)
async def create_blog(blog: schemas.BlogCreate):
    return await services.blog.create_blog(blog=blog)

@router.get("/{blog_id}", response_model=schemas.Blog)
async def get_blog(blog_id: str):
    blog = await services.blog.get_blog(blog_id=blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.put("/{blog_id}", response_model=schemas.Blog)
async def update_blog(blog_id: str, blog: schemas.BlogUpdate):
    updated_blog = await services.blog.update_blog(blog_id=blog_id, blog=blog)
    if updated_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return updated_blog

@router.delete("/{blog_id}")
async def delete_blog(blog_id: str):
    success = await services.blog.delete_blog(blog_id=blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted successfully"} 