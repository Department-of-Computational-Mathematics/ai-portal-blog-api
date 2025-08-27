from typing import List, Union
from fastapi import APIRouter, Query, Depends
from app.schemas.blog import BlogPost, Comment, Reply, AllBlogsBlogPost, BlogPostWithUserData, CommentBase, ReplyBase, UpdateTextRequest, LikeRequest, LikeResponse, LikeStatusResponse
from app.schemas.blog import KeycloakUser
from app.services.blog import create_blog, delete_blog_by_id, delete_comment_reply, fetch_comments_and_replies, get_all_blogs, get_blog_by_id, get_blogs_byTags, reply_comment, update_Comment_Reply, update_blog, write_comment, toggle_like, check_user_like_status
from app.services.keycloak import get_all_users, get_user_by_id
from app.core.security import get_current_user_id

router = APIRouter()

# Health check endpoint for blog service
@router.get("/health", tags=["Health"], summary="Blog Service Health Check")
async def blog_service_health():
    return {
        "service": "blog-service",
        "status": "up",
    }

# NOTE: DO NOT turn these `keycloak` endpoints on in production. These can leak user information !!
# ============================================
@router.get("/keycloak-users", response_model=List[KeycloakUser], tags=["Keycloak"], summary="Get all Keycloak users", deprecated=True)
async def getAllUsers():
    return get_all_users()


@router.get("/keycloak-users/{user_id}", response_model=KeycloakUser, tags=["Keycloak"], summary="Get Keycloak user by ID", deprecated=True)
async def getUserByID(user_id: str):
    return get_user_by_id(user_id)
# ============================================

# NOTE: All endpoints with `Authenticated` tag require `X-User-ID` header to be set with the user's ID.

@router.get('/blogs', response_model=List[AllBlogsBlogPost], tags=["Blog", "Unauthenticated"], summary="Get all blogs")
async def getAllBlogs():
    return await get_all_blogs()

@router.get('/blogsByTags', response_model=List[AllBlogsBlogPost], tags=["Blog", "Unauthenticated"], summary="Get blogs by tags")
async def Blogs_By_tags(tags : List[str]=Query(..., description="List of tags")): #Query(..., description="List of tags") added to make get request correctly as it includes tag numbers 
    return await get_blogs_byTags(tags)

@router.get("/blog/{blog_id}", response_model=BlogPostWithUserData ,tags=["Blog", "Unauthenticated"], summary="Get Blog by ID")
async def get_blog_by_blog_id(blog_id: str): #data type change from int to str
    blog = await get_blog_by_id(blog_id) #{"p_id": blog_id} => blog_id -function parameter error,parameter was not in format used in get_blog_by_id()
    return blog

@router.post('/createblog', response_model=BlogPostWithUserData, tags=["Blog", "Authenticated"], summary="Create a new blog post")
async def createBlog(blog: BlogPost, current_user_id: str = Depends(get_current_user_id)):
    # setting the user_id from the server-side. No need to pass it from the client side. (siginificantly more secure)
    blog.user_id = current_user_id
    return await create_blog(blog)

@router.put('/updateblog/{id}', response_model=BlogPostWithUserData, tags=["Blog", "Authenticated"], summary="Update an existing blog post")
async def updateBlog(id: str, blog: BlogPost, current_user_id: str = Depends(get_current_user_id)):
    blog.user_id = current_user_id  # Ensure the user_id is set from the server-side
    blog.blogPost_id = id  # Set the blog ID from the path parameter
    return await update_blog(blog)


@router.delete('/blogs/{id}', response_model=BlogPostWithUserData, tags=["Blog", "Authenticated"], summary="Delete a blog post by ID")
async def deleteBlog(id: str, current_user_id: str = Depends(get_current_user_id)):
    return await delete_blog_by_id(id, current_user_id)

@router.get('/blog/{id}/comments', response_model=List[CommentBase], tags=["Blog-Comment", "Unauthenticated"], summary="Get all comments and replies for a blog post")
async def get_comments_and_replies(id:str):
    return await fetch_comments_and_replies(id)

@router.post('/write-comment', response_model=CommentBase, tags=["Blog-Comment", "Authenticated"], summary="Write a comment on a blog post")
async def writeComment(comment: Comment, current_user_id: str = Depends(get_current_user_id)):
    # Server side setting - more secure
    comment.user_id = current_user_id
    return await write_comment(comment)

@router.post('/reply-comment', response_model=ReplyBase, tags=["Blog-Comment", "Authenticated"], summary="Reply to a comment on a blog post")
async def replyComment(reply: Reply, current_user_id: str = Depends(get_current_user_id)):
    # Server side setting - more secure
    reply.user_id = current_user_id
    return await reply_comment(reply)

@router.put('/edit-comment-reply/{id}', response_model=Union[CommentBase, ReplyBase], tags=["Blog-Comment", "Authenticated"], summary="Update a comment or reply")
async def updateCommentReply(id: str, request: UpdateTextRequest, current_user_id: str = Depends(get_current_user_id)):
    # for the simple text update, we have to use a schema, otherwise FastAPI defaults to considering the `request` in string as a query param
    return await update_Comment_Reply(id, request.text, current_user_id)

@router.delete('/delete-comment-reply/{id}', tags=["Blog-Comment", "Authenticated"], summary="Delete a comment or reply")
async def deleteCommentReply(id: str, current_user_id: str = Depends(get_current_user_id)):
    return await delete_comment_reply(id, current_user_id)

@router.post('/blog/{blog_id}/like', response_model=LikeResponse, tags=["Blog", "Authenticated"], summary="Like or unlike a blog post")
async def like_unlike_blog(blog_id: str, like_request: LikeRequest, current_user_id: str = Depends(get_current_user_id)):
    """
    Like or unlike a blog post.
    - like_value: 0 to unlike, 1 to like
    """
    return await toggle_like(blog_id, current_user_id, like_request.like_value)

@router.get('/blog/{blog_id}/like-status', response_model=LikeStatusResponse, tags=["Blog", "Authenticated"], summary="Check if user has liked a blog post")
async def get_user_like_status(blog_id: str, current_user_id: str = Depends(get_current_user_id)):
    """
    Check if the current user has liked a specific blog post.
    Returns like status, total likes count, and like details if applicable.
    """
    return await check_user_like_status(blog_id, current_user_id)

