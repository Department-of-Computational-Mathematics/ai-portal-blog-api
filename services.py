import json
from uuid import UUID
from fastapi import HTTPException
from bson import ObjectId,json_util
from database import collection_blog, collection_comment, collection_reply
from models import BlogPost, Comment, Reply
from typing import List


def initial_service():
    return {"Ping":"Pong"}


async def get_blog_by_id(entity_id: str): #data type changed from int to str
    try:
        entity = await collection_blog.find_one({"_id": entity_id}) #blogPost_id to _id , becaue in models.py ,"blogPost_id" changed to "_id" by  " alias="_id" "
        if entity is None:
            return {"message": f"Blog with id {entity_id} not found"}
        else:
            json_data = json.loads(json_util.dumps(entity))
            return json_data
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_blog(blog):
    blog_dict = blog.dict(by_alias=True) # added this part because dictionary data type should be used for insert_one as parametre
    result = await collection_blog.insert_one(blog_dict)
    if result.inserted_id:
        return blog
    raise HTTPException(400, "Blog Insertion failed")


async def update_blog(id, title, content, tags):
    # try:
    #     objId = ObjectId(id)
    # except:
    #     raise HTTPException(400, "Invalid Id format")
    # id type changed to str, so just store as str 
    result = await collection_blog.update_one(
        {"_id":id}, #objID to id and also blogPost_id to _id because in models.py ,"blogPost_id" changed to "_id" by  " alias="_id" "
        {"$set":{"title":title, "content":content, "tags":tags}}
    )

    if result.modified_count == 1:
        blog = await collection_blog.find_one({"_id":id}) #objID to id also blogPost_id to _id because in models.py ,"blogPost_id" changed to "_id" by  " alias="_id" "
        return blog
    elif result.modified_count == 0:
        raise HTTPException(404, "Blog not found")
    
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



async def get_all_blogs():
    # function need to be async to use 'async for' loop
    blogs = []
    cursor = collection_blog.find({})
    async for blog in cursor:
        blog["blogPost_id"] = str(blog["_id"])
        del blog["_id"]
        blogs.append(blog)
    if len(blogs) == 0:
        raise HTTPException(404, "No blogs found")
    return blogs
    

async def delete_blog_by_id(id: str):
    result = await collection_blog.delete_one({'_id': id}) #_id,  because in models.py ,"blogPost_id" changed to "_id" by  " alias="_id" "
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    return {"message": "Blog deleted successfully"}

async def get_blogs_byTags(tags : List[int]):
    blogs=[]
    if await collection_blog.count_documents({"tags": {"$in": tags}}) == 0: # await added because httpException didnt work due to have no enough time to count.
        raise HTTPException(status_code=404, detail="no blogs found with the given tags.")
    cursor=collection_blog.find({"tags": {"$in": tags}}) 
    async for document in cursor: # added async
        blogs.append(BlogPost(**document))
    return blogs


async def fetch_replies(parent_content_id: str): #uuid to str ,models.py -> blogPost_id changed from uuid to str
    replies_cursor = collection_reply.find({"parentContent_id": parent_content_id}) #await removed, TypeError: object AsyncIOMotorCursor can't be used in 'await' expression 
    replies = [Reply(**reply) async for reply in replies_cursor]
    
    # Recursively fetch replies for each reply
    for reply in replies:
        reply.replies = await fetch_replies(reply.reply_id) #added an attribute to the model.py -> "Reply" to store replies since reply.replies called here
    
    return replies


async def fetch_comments_and_replies(id: str):
    # try:
    #     objId = ObjectId(id)
    # except:
    #     raise HTTPException(400, "Invalid Id format")
     # id type changed to str, so just store as str 
    comments_cursor = collection_comment.find({"blogPost_id": id}) #objid to id , await removed - TypeError: object AsyncIOMotorCursor can't be used in 'await' expression 
    comments = [Comment(**comment) async for comment in comments_cursor]
    
    if len(comments)==0 :
        raise HTTPException(404, "Comments not found")
        
    # Fetch replies for each comment
    for comment in comments:
        comment.replies = await fetch_replies(comment.comment_id)#added an attribute to the model.py "Comment" to store replies since comment.replies called here
    
    return comments

async def update_Comment_Reply(id:str, text:str):
    #First search in comments collection
    comment = await collection_comment.find_one({"_id": id})
    if comment:
        result = await collection_comment.update_one(
            {"_id": id},
            {"$set": {"text": text}}
        )
        if result.modified_count == 1:
            updated_comment = await collection_comment.find_one({"_id": id})
            return updated_comment
        raise HTTPException(400, "Comment update failed")
    
    #If it is not in comment collection, then search in reply collection
    reply = await collection_reply.find_one({"_id":id})
    if reply:
        result = await collection_reply.update_one(
            {"_id":id},
            {"$set": {"text":text}}
        )
        if result.modified_count == 1:
            updated_reply = await collection_reply.find_one({"_id": id})
            return updated_reply
        raise HTTPException(400, "Reply update failed")
    
    raise HTTPException(404, "Comment or Reply not found")

async def delete_comment_reply(id):
    #First search in comments collection
    comment = await collection_comment.find_one({"_id": id})
    if comment:
        result = await collection_comment.delete_one({'_id': id})

        # Delete all replies associated with the comment
        result_ = await collection_reply.delete_many({'parentContent_id': id})
        if result.deleted_count == 0:
            raise HTTPException(400, "Comment deletion failed")
        return {"message": "Comment deleted successfully"}
    
    #If it is not in comment collection, then search in reply collection
    reply = await collection_reply.find_one({"_id":id})
    if reply:
        result = await collection_reply.delete_one({'_id': id})

        # Delete all replies associated with the reply
        result_ = await collection_reply.delete_many({'parentContent_id': id})
        if result.deleted_count == 0:
            raise HTTPException(400, "Reply deletion failed")
        return {"message": "Reply deleted successfully"}
    
    raise HTTPException(404, "Comment or Reply not found")