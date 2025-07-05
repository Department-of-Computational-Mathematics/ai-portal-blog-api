  
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import List, Optional
from datetime import datetime

class BlogPost(BaseModel): #represents a single blog post
    blogPost_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")    #blogPost_id:UUID = Field(default_factory=uuid4, alias="_id") #primary key
    comment_constraint:bool #whether commenting is enabled or not, if enabled then true
    tags:List[int]  # List of integers indicating relavant tags (topics)
    number_of_views:int
    title:str #topic of the blog
    content:str #content of the blog : just texts here, didnt handle images/videos in the blog post
    postedAt:datetime = Field(default_factory=datetime.utcnow) #posted date time -utc time
    post_image: Optional[str] = None  # Optional image URL for the blog post, can be null if no image is provided
    user_id: Optional[str] = None   #UUID to str ,author`s user_id - Optional for request, set server-side

class BlogPostWithUserData(BlogPost):
    user_display_name: Optional[str]  # Username of the author, can be null if not provided
    user_image: Optional[str] = None  # Optional image URL for the author, can be null if no image is provided

class AllBlogsBlogPost(BaseModel): #represents a single blog post with only essential fields for listing
    blogPost_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")    #blogPost_id:UUID = Field(default_factory=uuid4, alias="_id") #primary key
    comment_constraint:bool #whether commenting is enabled or not, if enabled then true
    tags:List[int]  # List of integers indicating relavant tags (topics)
    number_of_views:int
    title:str #topic of the blog
    content_preview:str # content preview of the blog, just texts here, didnt handle images/videos in the blog post
    postedAt:datetime = Field(default_factory=datetime.utcnow) #posted date time -utc time
    post_image: Optional[str] = None  # Optional image URL for the blog post, can be null if no image is provided
    user_id: Optional[str] = None   #UUID to str ,author`s user_id - Optional for request, set server-side
    user_display_name: Optional[str]  # Username of the author, can be null if not provided
    user_image: Optional[str] = None  # Optional image URL for the author, can be null if no image is provided

class Comment(BaseModel):
    comment_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")#UUID = Field(default_factory=uuid4, alias="_id") #primary key
    user_id: Optional[str] = None #UUID to str ,commenting person`s user_id - Optional for request, set server-side
    blogPost_id:str #UUID to str 
    text:str #comment content
    commentedAt:datetime = Field(default_factory=datetime.utcnow) #commented date time -utc time
    replies: List['Reply'] = [] #for fetch_comments_and_replies() function

class Reply(BaseModel):
    reply_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")#UUID = Field(default_factory=uuid4, alias="_id") #primary key
    parentContent_id:str #UUID to str ,either a comment_id or reply_id (when someone reply to an existing reply)
    user_id: Optional[str] = None #UUID to str, replying person`s` user_id - Optional for request, set server-side
    text:str #reply content
    repliedAt:datetime = Field(default_factory=datetime.utcnow) #replied date time -utc time
    replies: List['Reply'] = []  #for fetch_comments_and_replies() function
