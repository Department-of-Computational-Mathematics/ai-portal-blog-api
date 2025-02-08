from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.schemas import blog as blog_schema
from app.db.database import collection_blog

async def get_blog(blog_id: str) -> Optional[dict]:
    if not ObjectId.is_valid(blog_id):
        return None
    blog = await collection_blog.find_one({"_id": ObjectId(blog_id)})
    return blog

async def get_blogs(skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = collection_blog.find().skip(skip).limit(limit)
    blogs = await cursor.to_list(length=limit)
    return blogs

async def create_blog(blog: blog_schema.BlogCreate) -> dict:
    blog_dict = blog.dict()
    blog_dict["created_at"] = datetime.utcnow()
    blog_dict["updated_at"] = datetime.utcnow()
    
    result = await collection_blog.insert_one(blog_dict)
    created_blog = await collection_blog.find_one({"_id": result.inserted_id})
    return created_blog

async def update_blog(blog_id: str, blog: blog_schema.BlogUpdate) -> Optional[dict]:
    if not ObjectId.is_valid(blog_id):
        return None
        
    update_data = {
        k: v for k, v in blog.dict(exclude_unset=True).items() if v is not None
    }
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await collection_blog.update_one(
            {"_id": ObjectId(blog_id)},
            {"$set": update_data}
        )
    
    updated_blog = await collection_blog.find_one({"_id": ObjectId(blog_id)})
    return updated_blog

async def delete_blog(blog_id: str) -> bool:
    if not ObjectId.is_valid(blog_id):
        return False
        
    result = await collection_blog.delete_one({"_id": ObjectId(blog_id)})
    return result.deleted_count > 0 