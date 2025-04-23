  
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import List
from datetime import datetime

class BlogPost(BaseModel): #represents a single blog post
    blogPost_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")    #blogPost_id:UUID = Field(default_factory=uuid4, alias="_id") #primary key
    user_id:str   #UUID to str ,author`s user_id
    comment_constraint:bool #whether commenting is enabled or not, if enabled then true
    tags:List[int]  # List of integers indicating relavant tags (topics)
    number_of_views:int
    title:str #topic of the blog
    content:str #content of the blog : just texts here, didnt handle images/videos in the blog post
    postedAt:datetime = Field(default_factory=datetime.utcnow) #posted date time -utc time

class Comment(BaseModel):
    comment_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")#UUID = Field(default_factory=uuid4, alias="_id") #primary key
    user_id:str #UUID to str ,commenting person`s user_id
    blogPost_id:str #UUID to str 
    text:str #comment content
    commentedAt:datetime = Field(default_factory=datetime.utcnow) #commented date time -utc time
    replies: List['Reply'] = [] #for fetch_comments_and_replies() function

class Reply(BaseModel):
    reply_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")#UUID = Field(default_factory=uuid4, alias="_id") #primary key
    parentContent_id:str #UUID to str ,either a comment_id or reply_id (when someone reply to an existing reply)
    user_id:str #UUID t str, replying person`s` user_id
    text:str #reply content
    repliedAt:datetime = Field(default_factory=datetime.utcnow) #replied date time -utc time
    replies: List['Reply'] = []  #for fetch_comments_and_replies() function
