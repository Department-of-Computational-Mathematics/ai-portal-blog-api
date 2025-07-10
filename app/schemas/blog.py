from pydantic import BaseModel, Field
from uuid import uuid4
from typing import List, Optional
from datetime import datetime

# Base schemas without auto-generated IDs (for reading from DB)
class BlogPostBase(BaseModel): 
    blogPost_id: str = Field(alias="_id", serialization_alias="blog_id")  # No default_factory, expects existing ID
    comment_constraint: bool
    tags: List[str]
    number_of_views: int
    likes_count: int = 0
    title: str
    content: str
    postedAt: datetime
    post_image: Optional[str] = None
    user_id: Optional[str] = None

class CommentBase(BaseModel):
    comment_id: str = Field(alias="_id", serialization_alias="comment_id")  # No default_factory, expects existing ID
    user_id: Optional[str] = None
    user_display_name: Optional[str] = None
    user_profile_image: Optional[str] = None
    blogPost_id: str
    text: str
    commentedAt: datetime
    replies: List['ReplyBase'] = []

class ReplyBase(BaseModel):
    reply_id: str = Field(alias="_id", serialization_alias="reply_id")  # No default_factory, expects existing ID
    parentContent_id: str
    user_id: Optional[str] = None
    user_display_name: Optional[str] = None
    user_profile_image: Optional[str] = None
    text: str
    repliedAt: datetime
    replies: List['ReplyBase'] = []

# Request schemas with auto-generated IDs (for creating new records)
class BlogPost(BaseModel): 
    blogPost_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    comment_constraint: bool
    tags: List[str]
    number_of_views: int
    likes_count: int = 0
    title: str
    content: str
    postedAt: datetime = Field(default_factory=datetime.utcnow)
    post_image: Optional[str] = None
    user_id: Optional[str] = None

class Comment(BaseModel):
    comment_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: Optional[str] = None
    blogPost_id: str
    text: str
    commentedAt: datetime = Field(default_factory=datetime.utcnow)
    replies: List['Reply'] = []

class Reply(BaseModel):
    reply_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    parentContent_id: str #UUID to str ,either a comment_id or reply_id (when someone reply to an existing reply)
    user_id: Optional[str] = None
    text: str
    repliedAt: datetime = Field(default_factory=datetime.utcnow)
    replies: List['Reply'] = []

# Request models for updating content
class UpdateTextRequest(BaseModel):
    text: str

# Like model for blog likes
class Like(BaseModel):
    like_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    blog_id: str
    user_id: str
    liked_at: datetime = Field(default_factory=datetime.utcnow)

class LikeRequest(BaseModel):
    like_value: int = Field(..., ge=0, le=1, description="0 to unlike, 1 to like")

# Response schemas extending base schemas
class BlogPostWithUserData(BlogPostBase):
    user_display_name: Optional[str]
    user_image: Optional[str] = None

class AllBlogsBlogPost(BaseModel): 
    blogPost_id: str = Field(alias="_id", serialization_alias="blog_id")  # No default_factory, expects existing ID
    comment_constraint: bool
    tags: List[str]
    number_of_views: int
    likes_count: int = 0
    title: str
    content_preview: str
    postedAt: datetime
    post_image: Optional[str] = None
    user_id: Optional[str] = None
    user_display_name: Optional[str]
    user_image: Optional[str] = None

# Response models for like endpoints
class LikeResponse(BaseModel):
    message: str
    liked: bool

class LikeStatusResponse(BaseModel):
    blog_id: str
    user_id: str
    is_liked: bool
    likes_count: int
    like_id: Optional[str] = None
    liked_at: Optional[datetime] = None

# NOTE: alias is input for serialization, serialization_alias is output for serialization.