# Authentication System

## Overview

This blog API now implements user-based authorization to ensure users can only edit/delete their own content.

## How it Works

### Authentication Header

The system expects a `X-User-ID` header in requests that require authentication. This header should contain the user ID extracted from a JWT token by your API gateway.

```bash
# Example request
curl -X PUT "http://localhost:8000/api/v1/updateblog/123" \
  -H "X-User-ID: user123" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "content": "Updated content", "tags": [1,2]}'
```

### Authorization Levels

#### Authenticated (`get_current_user_id`)

These endpoints require the `X-User-ID` header:

- `POST /createblog` - Creates a blog (user_id auto-assigned)
- `PUT /updateblog/{id}` - Updates a blog (only owner can edit)
- `DELETE /blogs/{id}` - Deletes a blog (only owner can delete)
- `POST /write-comment` - Creates a comment (user_id auto-assigned)
- `POST /reply-comment` - Creates a reply (user_id auto-assigned)
- `PUT /edit-comment-reply/{id}` - Edits comment/reply (only owner can edit)
- `DELETE /delete-comment-reply/{id}` - Deletes comment/reply (only owner can delete)

#### Unauthenticated

These endpoints work without authentication but provide enhanced features when authenticated:

- `GET /blog/{blog_id}` - View blog
- `GET /blogs` - List all blogs
- `GET /blogsByTags` - Get blogs by tags
- `GET /blog/{id}/comments` - Get comments and replies

### Error Responses

#### 401 Unauthorized

When `X-User-ID` header is missing for required endpoints:

```json
{
  "detail": "User authentication required. X-User-ID header missing."
}
```

#### 403 Forbidden

When trying to edit/delete content belonging to another user:

```json
{
  "detail": "Permission denied. You can only edit your own blogs."
}
```

### Security Features

1. **Ownership Validation**: Users can only modify their own content
2. **Automatic User Assignment**: User IDs are automatically assigned from authentication
3. **Cascading Deletes**: Deleting a blog removes all associated comments and replies
4. **Nested Reply Protection**: Deleting a comment/reply also removes nested replies

## Gateway Integration

Your API gateway should:

1. Decode the JWT token to extract the user ID
2. Include the `X-User-ID` header in API requests
3. Handle 401/403 errors appropriately

## Database Schema

Make sure your MongoDB documents include the `user_id` field:

- `blogs` collection: `user_id` field
- `comments` collection: `user_id` field  
- `replies` collection: `user_id` field
