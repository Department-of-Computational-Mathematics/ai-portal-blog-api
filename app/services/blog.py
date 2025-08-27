import json
from fastapi import HTTPException
from bson import json_util
from app.db.database import collection_blog, collection_comment, collection_reply, collection_like, database
from app.schemas.blog import BlogPost, Comment, Reply, BlogPostWithUserData, AllBlogsBlogPost, CommentBase, ReplyBase, Like, BlogPostCreate, BlogPostUpdate, CommentCreate, ReplyCreate
from app.services.keycloak import get_user_by_id_safely
from app.core.exceptions import *
from typing import List, Dict

CONTENT_PREVIEW_LENGTH = 150  # Length of content preview for AllBlogsBlogPost

def convert_mongo_doc_to_dict(doc):
    """Convert MongoDB document to dict compatible with Pydantic models"""
    if doc is None:
        return None
    
    # Convert ObjectId and other MongoDB types to string/dict
    doc_dict = json.loads(json_util.dumps(doc))
    
    # Convert MongoDB datetime format to ISO string
    if 'postedAt' in doc_dict and isinstance(doc_dict['postedAt'], dict) and '$date' in doc_dict['postedAt']:
        doc_dict['postedAt'] = doc_dict['postedAt']['$date']
    
    if 'commentedAt' in doc_dict and isinstance(doc_dict['commentedAt'], dict) and '$date' in doc_dict['commentedAt']:
        doc_dict['commentedAt'] = doc_dict['commentedAt']['$date']
        
    if 'repliedAt' in doc_dict and isinstance(doc_dict['repliedAt'], dict) and '$date' in doc_dict['repliedAt']:
        doc_dict['repliedAt'] = doc_dict['repliedAt']['$date']
    
    return doc_dict

async def get_blog_by_id(entity_id: str) -> BlogPostWithUserData: #data type changed from int to str
    try:
        entity = await collection_blog.find_one({"_id": entity_id}) #blogPost_id to _id , becaue in models.py ,"blogPost_id" changed to "_id" by  " alias="_id" "

        # Convert MongoDB document to BlogPostWithUserData
        blog_data = convert_mongo_doc_to_dict(entity)
        if not blog_data:
            raise BlogNotFoundException(entity_id)

        # INFO: Design decision: current view is not considered for the view count. Idea is user want to know how many previous views
        # Increment the number_of_views by 1
        await collection_blog.update_one(
            {"_id": entity_id},
            {"$inc": {"number_of_views": 1}}
        )
        
        # Inject data from keycloak
        user_data = await get_user_by_id_safely(blog_data["user_id"])
        blog_data["user_username"] = user_data.username
        blog_data["user_image_url"] = user_data.profilePicUrl
        blog_data["user_first_name"] = user_data.firstName
        blog_data["user_last_name"] = user_data.lastName
        return BlogPostWithUserData(**blog_data)
    
    except BlogAPIException:
        # Re-raise the custom exceptions (like BlogNotFoundException)
        raise

    except Exception as e:
        print(f"An error occurred: {e}")
        raise InternalServerException


async def create_blog(blog_input: BlogPostCreate, user_id: str) -> BlogPostWithUserData:
    # Create a full BlogPost with auto-generated ID and default values
    blog = BlogPost(
        comment_constraint=blog_input.comment_constraint,
        tags=blog_input.tags,
        title=blog_input.title,
        content=blog_input.content,
        post_image=blog_input.post_image,
        user_id=user_id,
        number_of_views=0,  # Initialize to 0 for new blogs
        likes_count=0       # Initialize to 0 for new blogs
    )
    
    blog_dict = blog.dict(by_alias=True) # Backend controls the ID generation
    result = await collection_blog.insert_one(blog_dict)
    if result.inserted_id:
        # Convert BlogPost to BlogPostWithUserData for response
        blog_data = blog.dict(by_alias=True)  # Use by_alias=True to get _id instead of blogPost_id

        # Inject data from keycloak
        user_data = await get_user_by_id_safely(blog_data["user_id"])
        blog_data["user_username"] = user_data.username
        blog_data["user_image_url"] = user_data.profilePicUrl
        blog_data["user_first_name"] = user_data.firstName
        blog_data["user_last_name"] = user_data.lastName
        return BlogPostWithUserData(**blog_data)
    raise BlogInsertionException


async def update_blog(blog_id: str, blog_update: BlogPostUpdate, user_id: str) -> BlogPostWithUserData:
    # First check if blog exists and user owns it
    old_blog = await collection_blog.find_one({"_id": blog_id})
    if not old_blog:
        raise BlogNotFoundException(blog_id)

    if old_blog["user_id"] != user_id:
        raise BlogOwnershipException

    # Only update the fields that users are allowed to modify
    update_data = {
        "title": blog_update.title,
        "content": blog_update.content,
        "tags": blog_update.tags,
        "comment_constraint": blog_update.comment_constraint,
        "post_image": blog_update.post_image
    }
    
    result = await collection_blog.update_one(
        {"_id": blog_id}, 
        {"$set": update_data}
    )

    if result.modified_count == 1:
        updated_blog = await collection_blog.find_one({"_id": blog_id})
        # Convert to BlogPostWithUserData
        blog_data = convert_mongo_doc_to_dict(updated_blog)
        if blog_data is None:
            raise BlogUpdateException
        
        # Inject data from keycloak
        user_data = await get_user_by_id_safely(blog_data["user_id"])
        blog_data["user_username"] = user_data.username
        blog_data["user_image_url"] = user_data.profilePicUrl
        blog_data["user_first_name"] = user_data.firstName
        blog_data["user_last_name"] = user_data.lastName
        return BlogPostWithUserData(**blog_data)
    raise BlogUpdateException

async def write_comment(comment_input: CommentCreate, user_id: str) -> CommentBase:
    # Create a full Comment with auto-generated ID and timestamp
    comment = Comment(
        blogPost_id=comment_input.blogPost_id,
        text=comment_input.text,
        user_id=user_id
    )
    
    comment_dict = comment.dict(by_alias=True) # Backend controls the ID generation
    
    # Check if the blog post exists before allowing comment
    blog_exists = await collection_blog.find_one({"_id": comment_dict["blogPost_id"]})
    if not blog_exists:
        raise BlogNotFoundException(comment_dict["blogPost_id"])

    result = await collection_comment.insert_one(comment_dict)
    if result.inserted_id:
        # Return the comment from database as CommentBase to match response model
        created_comment = await collection_comment.find_one({"_id": comment_dict["_id"]})
        comment_data = convert_mongo_doc_to_dict(created_comment)
        if comment_data:
            # Inject data from keycloak
            user_data = await get_user_by_id_safely(comment_data["user_id"])
            comment_data["user_username"] = user_data.username
            comment_data["user_image_url"] = user_data.profilePicUrl
            comment_data["user_first_name"] = user_data.firstName
            comment_data["user_last_name"] = user_data.lastName
            return CommentBase(**comment_data)
    raise CommentInsertionException


async def reply_comment(reply_input: ReplyCreate, user_id: str):
    # Create a full Reply with auto-generated ID and timestamp
    reply = Reply(
        parentContent_id=reply_input.parentContent_id,
        text=reply_input.text,
        user_id=user_id
    )
    
    reply_dict = reply.dict(by_alias=True) # Backend controls the ID generation
    
    # Check if the parent comment or reply exists before allowing reply
    parent_exists = await collection_comment.find_one({"_id": reply_dict["parentContent_id"]})
    if not parent_exists:
        # If not found in comments, check in replies (for nested replies)
        parent_exists = await collection_reply.find_one({"_id": reply_dict["parentContent_id"]})
        if not parent_exists:
            raise ParentContentNotFoundException(reply_dict["parentContent_id"])

    result = await collection_reply.insert_one(reply_dict)
    if result.inserted_id:
        # Return the reply from database to match response model expectations
        created_reply = await collection_reply.find_one({"_id": reply_dict["_id"]})
        reply_data = convert_mongo_doc_to_dict(created_reply)
        if reply_data:
            # Inject data from keycloak
            user_data = await get_user_by_id_safely(reply_data["user_id"])
            reply_data["user_username"] = user_data.username
            reply_data["user_image_url"] = user_data.profilePicUrl
            reply_data["user_first_name"] = user_data.firstName
            reply_data["user_last_name"] = user_data.lastName
            return ReplyBase(**reply_data)
    raise ReplyInsertionException


async def get_all_blogs() -> List[AllBlogsBlogPost]:
    import asyncio
    # function need to be async to use 'async for' loop
    blogs = []
    user_data_cache = {}  # Cache user data to avoid duplicate requests
    
    cursor = collection_blog.find({})
    blog_list = []
    async for blog in cursor:
        blog_list.append(blog)
    
    # Extract unique user IDs
    unique_user_ids = list(set(blog.get("user_id") for blog in blog_list if blog.get("user_id")))
    
    # Fetch user data in parallel
    if unique_user_ids:
        user_data_tasks = [get_user_by_id_safely(user_id) for user_id in unique_user_ids]
        user_data_results = await asyncio.gather(*user_data_tasks)
        
        # Create cache mapping user_id to user_data
        for user_id, user_data in zip(unique_user_ids, user_data_results):
            user_data_cache[user_id] = user_data
    
    # Process blogs with cached user data
    for blog in blog_list:
        user_data = user_data_cache.get(blog.get("user_id"))
        if not user_data:
            # Fallback for missing user data
            user_data = await get_user_by_id_safely(blog.get("user_id", ""))
        
        # Convert BlogPost to AllBlogsBlogPost
        blog_data = {
            "_id": str(blog["_id"]),  # Use _id as the key since AllBlogsBlogPost uses alias="_id"
            "comment_constraint": blog["comment_constraint"],
            "tags": blog["tags"],
            "number_of_views": blog["number_of_views"],
            "likes_count": blog.get("likes_count", 0),  # Default to 0 for backward compatibility
            "title": blog["title"],
            "content_preview": blog["content"][:CONTENT_PREVIEW_LENGTH] + "..." if len(blog["content"]) > CONTENT_PREVIEW_LENGTH else blog["content"],  # Create preview from content
            "postedAt": blog["postedAt"],
            "post_image": blog.get("post_image"),
            "user_id": blog.get("user_id"),
            "user_username": user_data.username,
            "user_image_url": user_data.profilePicUrl,
            "user_first_name": user_data.firstName,
            "user_last_name": user_data.lastName
        }
        blogs.append(AllBlogsBlogPost(**blog_data))
    if len(blogs) == 0:
        raise NoBlogsFoundException()
    return blogs
    

async def delete_blog_by_id(id: str, user_id: str) -> BlogPostWithUserData:
    # First check if blog exists and user owns it
    blog = await collection_blog.find_one({"_id": id})
    if not blog:
        raise BlogNotFoundException(id)

    if blog["user_id"] != user_id:
        raise PermissionDeniedException()

    # Store blog data before deletion for return
    blog_data = convert_mongo_doc_to_dict(blog)
    if blog_data is None:
        raise BlogDeletionException()

    # Inject data from keycloak
    user_data = await get_user_by_id_safely(blog_data["user_id"])
    blog_data["user_username"] = user_data.username
    blog_data["user_image_url"] = user_data.profilePicUrl
    blog_data["user_first_name"] = user_data.firstName
    blog_data["user_last_name"] = user_data.lastName

    deleted_blog = BlogPostWithUserData(**blog_data)
    
    result = await collection_blog.delete_one({'_id': id})
    if result.deleted_count == 0:
        raise BlogDeletionException()
    
    # Also delete all comments and replies associated with this blog
    await collection_comment.delete_many({"blogPost_id": id})
    # Get all comment IDs for this blog to delete their replies
    comment_ids = [comment["_id"] async for comment in collection_comment.find({"blogPost_id": id})]
    if comment_ids:
        await collection_reply.delete_many({"parentContent_id": {"$in": comment_ids}})
    
    return deleted_blog


async def get_blogs_byTags(tags : List[str]) -> List[AllBlogsBlogPost]:
    blogs=[]
    if await collection_blog.count_documents({"tags": {"$in": tags}}) == 0: # await added because httpException didnt work due to have no enough time to count.
        raise BlogsByTagsNotFoundException(tags)
    cursor=collection_blog.find({"tags": {"$in": tags}}) 
    async for document in cursor: # added async
        # Inject data from keycloak
        user_data = await get_user_by_id_safely(document["user_id"])
        # Convert BlogPost to AllBlogsBlogPost
        blog_data = {
            "_id": str(document["_id"]),  # Use _id as the key since AllBlogsBlogPost uses alias="_id"
            "comment_constraint": document["comment_constraint"],
            "tags": document["tags"],
            "number_of_views": document["number_of_views"],
            "likes_count": document.get("likes_count", 0),  # Default to 0 for backward compatibility
            "title": document["title"],
            "content_preview": document["content"][:CONTENT_PREVIEW_LENGTH] + "..." if len(document["content"]) > 200 else document["content"],  # Create preview from content
            "postedAt": document["postedAt"],
            "post_image": document.get("post_image"),
            "user_id": document.get("user_id"),
            "user_username": user_data.username,
            "user_image_url": user_data.profilePicUrl,
            "user_first_name": user_data.firstName,
            "user_last_name": user_data.lastName
        }
        blogs.append(AllBlogsBlogPost(**blog_data))
    return blogs


async def fetch_replies(parent_content_id: str): #uuid to str ,models.py -> blogPost_id changed from uuid to str
    replies_cursor = collection_reply.find({"parentContent_id": parent_content_id}) #await removed, TypeError: object AsyncIOMotorCursor can't be used in 'await' expression 
    replies = []
    async for reply in replies_cursor:
        reply_data = convert_mongo_doc_to_dict(reply)
        if reply_data:
            # Inject data from keycloak
            user_data = await get_user_by_id_safely(reply_data["user_id"])
            reply_data["user_username"] = user_data.username
            reply_data["user_image_url"] = user_data.profilePicUrl
            reply_data["user_first_name"] = user_data.firstName
            reply_data["user_last_name"] = user_data.lastName
            reply_obj = ReplyBase(**reply_data)
            # Recursively fetch replies for each reply 
            # TODO: Any way to limit recursion depth or avoid recursion all together?
            reply_obj.replies = await fetch_replies(reply_obj.reply_id)
            replies.append(reply_obj)
    
    return replies


async def fetch_comments_and_replies(id: str):
    # try:
    #     objId = ObjectId(id)
    # except:
    #     raise HTTPException(400, "Invalid Id format")
     # id type changed to str, so just store as str 
    comments_cursor = collection_comment.find({"blogPost_id": id}) #objid to id , await removed - TypeError: object AsyncIOMotorCursor can't be used in 'await' expression 
    comments = []
    async for comment in comments_cursor:
        comment_data = convert_mongo_doc_to_dict(comment)
        if comment_data:
            # Inject data from keycloak
            user_data = await get_user_by_id_safely(comment_data["user_id"])
            comment_data["user_username"] = user_data.username
            comment_data["user_image_url"] = user_data.profilePicUrl
            comment_data["user_first_name"] = user_data.firstName
            comment_data["user_last_name"] = user_data.lastName
            comment_obj = CommentBase(**comment_data)
            # Fetch replies for each comment
            comment_obj.replies = await fetch_replies(comment_obj.comment_id)
            comments.append(comment_obj)
    
    if len(comments)==0 :
        raise NoCommentsFoundException()

    return comments

async def update_Comment_Reply(id: str, text: str, user_id: str):
    # First search in comments collection
    comment = await collection_comment.find_one({"_id": id})
    if comment:
        # Check if user owns this comment
        if comment["user_id"] != user_id:
            raise ReplyOwnershipException()
        
        result = await collection_comment.update_one(
            {"_id": id},
            {"$set": {"text": text}}
        )
        if result.modified_count == 1:
            updated_comment = await collection_comment.find_one({"_id": id})
            comment_data = convert_mongo_doc_to_dict(updated_comment)
            if comment_data:
                # Inject data from keycloak
                user_data = await get_user_by_id_safely(comment_data["user_id"])
                comment_data["user_username"] = user_data.username
                comment_data["user_image_url"] = user_data.profilePicUrl
                comment_data["user_first_name"] = user_data.firstName
                comment_data["user_last_name"] = user_data.lastName
                return CommentBase(**comment_data)
        raise CommentUpdateException()

    # If it is not in comment collection, then search in reply collection
    reply = await collection_reply.find_one({"_id": id})
    if reply:
        # Check if user owns this reply
        if reply["user_id"] != user_id:
            raise ReplyOwnershipException()

        result = await collection_reply.update_one(
            {"_id": id},
            {"$set": {"text": text}}
        )
        if result.modified_count == 1:
            updated_reply = await collection_reply.find_one({"_id": id})
            reply_data = convert_mongo_doc_to_dict(updated_reply)
            if reply_data:
                # Inject data from keycloak
                user_data = await get_user_by_id_safely(reply_data["user_id"])
                reply_data["user_username"] = user_data.username
                reply_data["user_image_url"] = user_data.profilePicUrl
                reply_data["user_first_name"] = user_data.firstName
                reply_data["user_last_name"] = user_data.lastName
                return ReplyBase(**reply_data)
        raise ReplyUpdateException()

    raise CommentOrReplyNotFoundException()


async def delete_comment_reply(id: str, user_id: str):
    # First search in comments collection
    comment = await collection_comment.find_one({"_id": id})
    if comment:
        # Check if user owns this comment
        if comment["user_id"] != user_id:
            raise PermissionDeniedException()
        
        result = await collection_comment.delete_one({'_id': id})
        # Delete all replies associated with the comment
        await collection_reply.delete_many({'parentContent_id': id})
        
        if result.deleted_count == 0:
            raise CommentDeletionException()
        return {"message": "Comment and associated replies deleted successfully"}
    
    # If it is not in comment collection, then search in reply collection
    reply = await collection_reply.find_one({"_id": id})
    if reply:
        # Check if user owns this reply
        if reply["user_id"] != user_id:
            raise PermissionDeniedException

        result = await collection_reply.delete_one({'_id': id})
        # Delete all replies associated with the reply (nested replies)
        await collection_reply.delete_many({'parentContent_id': id})
        
        if result.deleted_count == 0:
            raise ReplyDeletionException()
        return {"message": "Reply and nested replies deleted successfully"}

    raise CommentOrReplyNotFoundException()


async def like_or_unlike(blog_id: str, user_id: str, like_value: int):
    """
    Toggle like/unlike for a blog post.
    like_value: 0 to unlike, 1 to like
    """
    # First check if blog exists
    blog = await collection_blog.find_one({"_id": blog_id})
    if not blog:
        raise BlogNotFoundException(blog_id)

    # Check if user has already liked this blog
    existing_like = await collection_like.find_one({"blog_id": blog_id, "user_id": user_id})
    
    if like_value == 1:  # User wants to like the blog
        if existing_like:
            # Already liked - no action needed
            return {"message": "Blog already liked", "liked": True}
        else:
            # Create new like record
            like = Like(blog_id=blog_id, user_id=user_id)
            like_dict = like.dict(by_alias=True)
            result = await collection_like.insert_one(like_dict)
            if result.inserted_id:
                # Increment likes_count in blog post, handling case where field might not exist
                await collection_blog.update_one(
                    {"_id": blog_id},
                    [
                        {
                            "$set": {
                                "likes_count": {"$add": [{"$ifNull": ["$likes_count", 0]}, 1]}
                            }
                        }
                    ]
                )
                return {"message": "Blog liked successfully", "liked": True}
            else:
                raise BlogLikeException()
    elif like_value == 0:  # User wants to unlike the blog
        if existing_like:
            # Remove the like record
            result = await collection_like.delete_one({"blog_id": blog_id, "user_id": user_id})
            if result.deleted_count > 0:
                # Decrement likes_count in blog post, but ensure it doesn't go below 0
                await collection_blog.update_one(
                    {"_id": blog_id},
                    [
                        {
                            "$set": {
                                "likes_count": {
                                    "$max": [{"$subtract": [{"$ifNull": ["$likes_count", 0]}, 1]}, 0]
                                }
                            }
                        }
                    ]
                )
                return {"message": "Blog unliked successfully", "liked": False}
            else:
                raise BlogUnlikeException()
        else:
            # Already not liked - no action needed
            return {"message": "Blog not liked yet", "liked": False}
    
    else:
        raise InvalidLikeValueException()

async def check_user_like_status(blog_id: str, user_id: str):
    """
    Check if a user has liked a specific blog post.
    Returns the like status and blog information.
    """
    # First check if blog exists
    blog = await collection_blog.find_one({"_id": blog_id})
    if not blog:
        raise BlogNotFoundException(blog_id)

    # Check if user has liked this blog
    existing_like = await collection_like.find_one({"blog_id": blog_id, "user_id": user_id})
    
    return {
        "blog_id": blog_id,
        "user_id": user_id,
        "is_liked": existing_like is not None,
        "likes_count": blog.get("likes_count", 0),
        "like_id": str(existing_like["_id"]) if existing_like else None,
        "liked_at": existing_like.get("liked_at") if existing_like else None
    }

async def check_database_health() -> Dict:
    """
    Check MongoDB database health by performing basic operations and collecting metrics.
    Returns health status with response time and database metrics.
    """
    import time
    
    try:
        start_time = time.time()
        
        # Test database connection by running a simple ping
        await database.command("ping")
        
        # Get collection statistics
        blogs_count = await collection_blog.count_documents({})
        comments_count = await collection_comment.count_documents({})
        replies_count = await collection_reply.count_documents({})
        likes_count = await collection_like.count_documents({})
        
        # Calculate response time
        response_time = round((time.time() - start_time) * 1000, 2)  # Convert to milliseconds
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "service": "mongodb",
            "metrics": {
                "total_blogs": blogs_count,
                "total_comments": comments_count,
                "total_replies": replies_count,
                "total_likes": likes_count,
                "total_content_items": blogs_count + comments_count + replies_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time_ms": None,
            "service": "mongodb",
            "error": str(e),
            "metrics": None
        }