from typing import List, Union
from fastapi import APIRouter, Query, Depends
from app.schemas.blog import BlogPost, Comment, Reply
from app.services.blog import create_blog, delete_blog_by_id, delete_comment_reply, fetch_comments_and_replies, get_all_blogs, get_blog_by_id, get_blogs_byTags, reply_comment, update_Comment_Reply, update_blog, write_comment
from app.core.security import get_current_user_id

router = APIRouter()

@router.get("/blog/{blog_id}", tags=["Blog", "Unauthenticated"], summary="Get Blog by ID")
async def get_blog_by_blog_id(blog_id: str): #data type change from int to str
    blog = await get_blog_by_id(blog_id) #{"p_id": blog_id} => blog_id -function parameter error,parameter was not in format used in get_blog_by_id()
    return blog

@router.post('/createblog', response_model=BlogPost, tags=["Blog", "Authenticated"], summary="Create a new blog post")
async def createBlog(blog: BlogPost, current_user_id: str = Depends(get_current_user_id)):
    # setting the user_id from the server-side. No need to pass it from the client side. (siginificantly more secure)
    blog.user_id = current_user_id
    return await create_blog(blog)

@router.put('/updateblog/{id}', response_model=BlogPost, tags=["Blog", "Authenticated"], summary="Update an existing blog post")
async def updateBlog(id: str, title: str, content: str, tags: List[int] = Query(...), current_user_id: str = Depends(get_current_user_id)):
    return await update_blog(id, title, content, tags, current_user_id)

@router.post('/write-comment', response_model=Comment, tags=["Blog-Comment", "Authenticated"], summary="Write a comment on a blog post")
async def writeComment(comment: Comment, current_user_id: str = Depends(get_current_user_id)):
    # Server side setting - more secure
    comment.user_id = current_user_id
    return await write_comment(comment)

@router.post('/reply-comment', response_model=Reply, tags=["Blog-Comment", "Authenticated"], summary="Reply to a comment on a blog post")
async def replyComment(reply: Reply, current_user_id: str = Depends(get_current_user_id)):
    # Server side setting - more secure
    reply.user_id = current_user_id
    return await reply_comment(reply)

@router.get('/blogs', response_model=List[BlogPost], tags=["Blog", "Unauthenticated"], summary="Get all blogs")
async def getAllBlogs():
    return await get_all_blogs()

@router.delete('/blogs/{id}', tags=["Blog", "Authenticated"], summary="Delete a blog post by ID")
async def deleteBlog(id: str, current_user_id: str = Depends(get_current_user_id)):
    return await delete_blog_by_id(id, current_user_id)

@router.get('/blogsByTags',response_model=List[BlogPost], tags=["Blog", "Unauthenticated"], summary="Get blogs by tags")
async def Blogs_By_tags(tags : List[int]= Query(..., description="List of tags")): #Query(..., description="List of tags") added to make get request correctly as it includes tag numbers 
    return await get_blogs_byTags(tags)

@router.get('/blog/{id}/comments', response_model=List[Comment], tags=["Blog-Comment", "Unauthenticated"], summary="Get all comments and replies for a blog post")
async def get_comments_and_replies(id:str):
    return await fetch_comments_and_replies(id)

@router.put('/edit-comment-reply/{id}', response_model=Union[Comment, Reply], tags=["Blog-Comment", "Authenticated"], summary="Update a comment or reply")
async def updateCommentReply(id: str, text: str, current_user_id: str = Depends(get_current_user_id)):
    return await update_Comment_Reply(id, text, current_user_id)

@router.delete('/delete-comment-reply/{id}', tags=["Blog-Comment", "Authenticated"], summary="Delete a comment or reply")
async def deleteCommentReply(id: str, current_user_id: str = Depends(get_current_user_id)):
    return await delete_comment_reply(id, current_user_id)