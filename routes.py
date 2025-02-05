import json
from typing import List, Union
from fastapi import APIRouter,Depends,HTTPException,Query #query used for get_blogs_by_tag() function
from services import delete_comment_reply, fetch_comments_and_replies, initial_service,get_blogs_byTags,create_blog, update_Comment_Reply,update_blog, get_blog_by_id,delete_blog_by_id, get_all_blogs, reply_comment,  write_comment
from typing import List
from models import BlogPost,Comment, Reply




router=APIRouter()

@router.get('/')
async def getInitial():
    return initial_service()



@router.get("/blog/{blog_id}")
async def get_blog_by_blog_id(blog_id: str): #data type change from int to str
    entity = await get_blog_by_id(blog_id) #{"p_id": blog_id} => blog_id -function parameter error,parameter was not in format used in get_blog_by_id()
    return entity



@router.post('/createblog', response_model=BlogPost)
async def createBlog(blog: BlogPost):
    return await create_blog(blog)



@router.put('/updateblog/{id}', response_model=BlogPost)
async def updateBlog(id: str, title:str, content:str, tags:List[int]= Query(...)):
    return await update_blog(id, title, content, tags)


@router.post('/write-comment', response_model=Comment)
async def writeComment(comment: Comment):
    return await write_comment(comment)

@router.post('/reply-comment', response_model=Reply)
async def replyComment(reply: Reply):
    return await reply_comment(reply)



@router.get('/blogs', response_model=List[BlogPost])
async def getAllBlogs():
    return await get_all_blogs()


@router.delete('/blogs/{id}')
async def deleteBlog(id:str):
    return await delete_blog_by_id(id)


@router.get('/blogsByTags',response_model=List[BlogPost])
async def Blogs_By_tags(tags : List[int]= Query(..., description="List of tags")): #Query(..., description="List of tags") added to make get request correctly as it includes tag numbers 
    return await get_blogs_byTags(tags)


@router.get('/blog/{id}/comments', response_model=List[Comment])
async def get_comments_and_replies(id:str):
    return await fetch_comments_and_replies(id)

@router.put('/edit-comment-reply/{id}', response_model=Union[Comment, Reply])
async def updateCommentReply(id:str, text:str):
    return await update_Comment_Reply(id, text)

@router.delete('/delete-comment-reply/{id}')
async def deleteCommentReply(id:str):
    return await delete_comment_reply(id)