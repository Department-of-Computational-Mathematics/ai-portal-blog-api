from typing import List, Union
from fastapi import APIRouter, Query
from app.schemas.blog import BlogPost, Comment, Reply
from app.services.blog import create_blog, delete_blog_by_id, delete_comment_reply, fetch_comments_and_replies, get_all_blogs, get_blog_by_id, get_blogs_byTags, reply_comment, update_Comment_Reply, update_blog, write_comment

router = APIRouter()

@router.get("/blog/{blog_id}", tags=["Blog"])
async def get_blog_by_blog_id(blog_id: str): #data type change from int to str
    entity = await get_blog_by_id(blog_id) #{"p_id": blog_id} => blog_id -function parameter error,parameter was not in format used in get_blog_by_id()
    return entity

@router.post('/createblog', response_model=BlogPost, tags=["Blog"])
async def createBlog(blog: BlogPost):
    return await create_blog(blog)

@router.put('/updateblog/{id}', response_model=BlogPost, tags=["Blog"])
async def updateBlog(id: str, title:str, content:str, tags:List[int]= Query(...)):
    return await update_blog(id, title, content, tags)

@router.post('/write-comment', response_model=Comment, tags=["Blog-Comment"])
async def writeComment(comment: Comment):
    return await write_comment(comment)

@router.post('/reply-comment', response_model=Reply, tags=["Blog-Comment"])
async def replyComment(reply: Reply):
    return await reply_comment(reply)

@router.get('/blogs', response_model=List[BlogPost], tags=["Blog"])
async def getAllBlogs():
    return await get_all_blogs()

@router.delete('/blogs/{id}', tags=["Blog"])
async def deleteBlog(id:str):
    return await delete_blog_by_id(id)

@router.get('/blogsByTags',response_model=List[BlogPost], tags=["Blog"])
async def Blogs_By_tags(tags : List[int]= Query(..., description="List of tags")): #Query(..., description="List of tags") added to make get request correctly as it includes tag numbers 
    return await get_blogs_byTags(tags)

@router.get('/blog/{id}/comments', response_model=List[Comment], tags=["Blog-Comment"])
async def get_comments_and_replies(id:str):
    return await fetch_comments_and_replies(id)

@router.put('/edit-comment-reply/{id}', response_model=Union[Comment, Reply], tags=["Blog-Comment"])
async def updateCommentReply(id:str, text:str):
    return await update_Comment_Reply(id, text)

@router.delete('/delete-comment-reply/{id}', tags=["Blog-Comment"])
async def deleteCommentReply(id:str):
    return await delete_comment_reply(id)