import json
from fastapi import HTTPException
from bson import json_util
from app.db.database import collection_blog, collection_comment, collection_reply
from app.schemas.blog import BlogPost, Comment, Reply, BlogPostWithUserData, AllBlogsBlogPost, CommentBase, ReplyBase
from typing import List

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
        if entity is None:
            raise HTTPException(status_code=404, detail=f"Blog with id {entity_id} not found")
        
        # Convert MongoDB document to BlogPostWithUserData
        blog_data = convert_mongo_doc_to_dict(entity)
        if blog_data is None:
            raise HTTPException(status_code=404, detail=f"Blog with id {entity_id} not found")
        
        # Add dummy user data (to be populated later with actual user service logic)
        blog_data["user_display_name"] = "dummy_user"
        blog_data["user_image"] = "https://picsum.photos/200"
        return BlogPostWithUserData(**blog_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_blog(blog) -> BlogPostWithUserData:
    blog_dict = blog.dict(by_alias=True) # added this part because dictionary data type should be used for insert_one as parametre
    result = await collection_blog.insert_one(blog_dict)
    if result.inserted_id:
        # Convert BlogPost to BlogPostWithUserData for response
        blog_data = blog.dict(by_alias=True)  # Use by_alias=True to get _id instead of blogPost_id
        blog_data["user_display_name"] = "dummy_user"
        blog_data["user_image"] = "https://picsum.photos/200"
        return BlogPostWithUserData(**blog_data)
    raise HTTPException(400, "Blog Insertion failed")


async def update_blog(id, title, content, tags, user_id: str) -> BlogPostWithUserData:
    # First check if blog exists and user owns it
    blog = await collection_blog.find_one({"_id": id})
    if not blog:
        raise HTTPException(404, "Blog not found")
    
    if blog["user_id"] != user_id:
        raise HTTPException(403, "Permission denied. You can only edit your own blogs.")
    
    result = await collection_blog.update_one(
        {"_id":id}, 
        {"$set":{"title":title, "content":content, "tags":tags}}
    )

    if result.modified_count == 1:
        updated_blog = await collection_blog.find_one({"_id":id})
        # Convert to BlogPostWithUserData
        blog_data = convert_mongo_doc_to_dict(updated_blog)
        if blog_data is None:
            raise HTTPException(400, "Blog update failed")
        blog_data["user_display_name"] = "dummy_user"
        blog_data["user_image"] = "https://picsum.photos/200"
        return BlogPostWithUserData(**blog_data)
    
    raise HTTPException(400, "Blog update failed")


async def write_comment(comment):
    comment_dict = comment.dict(by_alias=True) # added this part because dictionary data type should be used for insert_one as parameter
    result = await collection_comment.insert_one(comment_dict)
    if result.inserted_id:
        return comment
    raise HTTPException(400, "Comment Insertion failed")

async def reply_comment(reply):
    reply_dict = reply.dict(by_alias=True) # added this part because dictionary data type should be used for insert_one as parameter
    result = await collection_reply.insert_one(reply_dict)
    if result.inserted_id:
        return reply
    raise HTTPException(400, "Reply Insertion failed")



async def get_all_blogs() -> List[AllBlogsBlogPost]:
    # function need to be async to use 'async for' loop
    blogs = []
    cursor = collection_blog.find({})
    async for blog in cursor:
        # Convert BlogPost to AllBlogsBlogPost
        blog_data = {
            "_id": str(blog["_id"]),  # Use _id as the key since AllBlogsBlogPost uses alias="_id"
            "comment_constraint": blog["comment_constraint"],
            "tags": blog["tags"],
            "number_of_views": blog["number_of_views"],
            "title": blog["title"],
            "content_preview": blog["content"][:CONTENT_PREVIEW_LENGTH] + "..." if len(blog["content"]) > 200 else blog["content"],  # Create preview from content
            "postedAt": blog["postedAt"],
            "post_image": blog.get("post_image"),
            "user_id": blog.get("user_id"),
            "user_display_name": "dummy_user",  # Dummy data
            "user_image": "https://picsum.photos/200"  # Dummy data
        }
        blogs.append(AllBlogsBlogPost(**blog_data))
    if len(blogs) == 0:
        raise HTTPException(404, "No blogs found")
    return blogs
    

async def delete_blog_by_id(id: str, user_id: str) -> BlogPostWithUserData:
    # First check if blog exists and user owns it
    blog = await collection_blog.find_one({"_id": id})
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    
    if blog["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Permission denied. You can only delete your own blogs.")
    
    # Store blog data before deletion for return
    blog_data = convert_mongo_doc_to_dict(blog)
    if blog_data is None:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    blog_data["user_display_name"] = "dummy_user"
    blog_data["user_image"] = "https://picsum.photos/200"
    deleted_blog = BlogPostWithUserData(**blog_data)
    
    result = await collection_blog.delete_one({'_id': id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    
    # Also delete all comments and replies associated with this blog
    await collection_comment.delete_many({"blogPost_id": id})
    # Get all comment IDs for this blog to delete their replies
    comment_ids = [comment["_id"] async for comment in collection_comment.find({"blogPost_id": id})]
    if comment_ids:
        await collection_reply.delete_many({"parentContent_id": {"$in": comment_ids}})
    
    return deleted_blog

async def get_blogs_byTags(tags : List[int]) -> List[AllBlogsBlogPost]:
    blogs=[]
    if await collection_blog.count_documents({"tags": {"$in": tags}}) == 0: # await added because httpException didnt work due to have no enough time to count.
        raise HTTPException(status_code=404, detail="no blogs found with the given tags.")
    cursor=collection_blog.find({"tags": {"$in": tags}}) 
    async for document in cursor: # added async
        # Convert BlogPost to AllBlogsBlogPost
        blog_data = {
            "_id": str(document["_id"]),  # Use _id as the key since AllBlogsBlogPost uses alias="_id"
            "comment_constraint": document["comment_constraint"],
            "tags": document["tags"],
            "number_of_views": document["number_of_views"],
            "title": document["title"],
            "content_preview": document["content"][:CONTENT_PREVIEW_LENGTH] + "..." if len(document["content"]) > 200 else document["content"],  # Create preview from content
            "postedAt": document["postedAt"],
            "post_image": document.get("post_image"),
            "user_id": document.get("user_id"),
            "user_display_name": "dummy_user",  # Dummy data
            "user_image": "https://picsum.photos/200"  # Dummy data
        }
        blogs.append(AllBlogsBlogPost(**blog_data))
    return blogs


async def fetch_replies(parent_content_id: str): #uuid to str ,models.py -> blogPost_id changed from uuid to str
    replies_cursor = collection_reply.find({"parentContent_id": parent_content_id}) #await removed, TypeError: object AsyncIOMotorCursor can't be used in 'await' expression 
    replies = []
    async for reply in replies_cursor:
        reply_data = convert_mongo_doc_to_dict(reply)
        if reply_data:
            reply_obj = ReplyBase(**reply_data)
            # Recursively fetch replies for each reply
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
            comment_obj = CommentBase(**comment_data)
            # Fetch replies for each comment
            comment_obj.replies = await fetch_replies(comment_obj.comment_id)
            comments.append(comment_obj)
    
    if len(comments)==0 :
        raise HTTPException(404, "Comments not found")
        
    return comments

async def update_Comment_Reply(id: str, text: str, user_id: str):
    # First search in comments collection
    comment = await collection_comment.find_one({"_id": id})
    if comment:
        # Check if user owns this comment
        if comment["user_id"] != user_id:
            raise HTTPException(403, "Permission denied. You can only edit your own comments.")
        
        result = await collection_comment.update_one(
            {"_id": id},
            {"$set": {"text": text}}
        )
        if result.modified_count == 1:
            updated_comment = await collection_comment.find_one({"_id": id})
            comment_data = convert_mongo_doc_to_dict(updated_comment)
            return CommentBase(**comment_data) if comment_data else None
        raise HTTPException(400, "Comment update failed")
    
    # If it is not in comment collection, then search in reply collection
    reply = await collection_reply.find_one({"_id": id})
    if reply:
        # Check if user owns this reply
        if reply["user_id"] != user_id:
            raise HTTPException(403, "Permission denied. You can only edit your own replies.")
        
        result = await collection_reply.update_one(
            {"_id": id},
            {"$set": {"text": text}}
        )
        if result.modified_count == 1:
            updated_reply = await collection_reply.find_one({"_id": id})
            reply_data = convert_mongo_doc_to_dict(updated_reply)
            return ReplyBase(**reply_data) if reply_data else None
        raise HTTPException(400, "Reply update failed")
    
    raise HTTPException(404, "Comment or Reply not found")

async def delete_comment_reply(id: str, user_id: str):
    # First search in comments collection
    comment = await collection_comment.find_one({"_id": id})
    if comment:
        # Check if user owns this comment
        if comment["user_id"] != user_id:
            raise HTTPException(403, "Permission denied. You can only delete your own comments.")
        
        result = await collection_comment.delete_one({'_id': id})
        # Delete all replies associated with the comment
        await collection_reply.delete_many({'parentContent_id': id})
        
        if result.deleted_count == 0:
            raise HTTPException(400, "Comment deletion failed")
        return {"message": "Comment and associated replies deleted successfully"}
    
    # If it is not in comment collection, then search in reply collection
    reply = await collection_reply.find_one({"_id": id})
    if reply:
        # Check if user owns this reply
        if reply["user_id"] != user_id:
            raise HTTPException(403, "Permission denied. You can only delete your own replies.")
        
        result = await collection_reply.delete_one({'_id': id})
        # Delete all replies associated with the reply (nested replies)
        await collection_reply.delete_many({'parentContent_id': id})
        
        if result.deleted_count == 0:
            raise HTTPException(400, "Reply deletion failed")
        return {"message": "Reply and nested replies deleted successfully"}
    
    raise HTTPException(404, "Comment or Reply not found")