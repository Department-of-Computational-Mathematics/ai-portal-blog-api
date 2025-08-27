"""
Reusable HTTP response schemas for API documentation.
Contains common error responses and endpoint-specific response combinations.
"""

from typing import Any, Dict

# ============================================================================
# ENDPOINT-SPECIFIC RESPONSES
# ============================================================================

# Health Check Responses
HEALTH_CHECK_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Service is healthy"},
    500: {"description": "Internal server error"}
}

# Keycloak Responses
KEYCLOAK_USERS_LIST_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Successfully retrieved list of Keycloak users"},
    401: {"description": "Unauthorized"},
    500: {"description": "Internal server error"}
}

KEYCLOAK_USER_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Successfully retrieved Keycloak user"},
    404: {"description": "Keycloak user not found"},
    401: {"description": "Unauthorized"},
    500: {"description": "Internal server error"}
}

# Blog List/Read Responses
BLOGS_LIST_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Successfully retrieved list of blogs"},
    404: {"description": "No blogs found"},
    500: {"description": "Internal server error"}
}

BLOGS_BY_TAGS_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Successfully retrieved blogs by tags"},
    404: {"description": "No blogs found for the given tags"},
    500: {"description": "Internal server error"}
}

BLOG_GET_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Successfully retrieved blog"},
    404: {"description": "Blog not found"},
    500: {"description": "Internal server error"}
}

# Blog CRUD Responses
BLOG_CREATE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    201: {"description": "Blog created successfully"},
    500: {"description": "Internal server error"}
}

BLOG_UPDATE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Blog updated successfully"},
    403: {"description": "Forbidden"},
    404: {"description": "Blog not found"},
    500: {"description": "Internal server error"}
}

BLOG_DELETE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Blog deleted successfully"},
    403: {"description": "Forbidden"},
    404: {"description": "Blog not found"},
    500: {"description": "Internal server error"}
}

# Comment/Reply Responses
COMMENTS_LIST_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Successfully retrieved comments"},
    404: {"description": "No comments found"},
    500: {"description": "Internal server error"}
}

COMMENT_CREATE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    201: {"description": "Comment created successfully"},
    404: {"description": "Blog not found"},
    500: {"description": "Internal server error"}
}

REPLY_CREATE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    201: {"description": "Reply created successfully"},
    404: {"description": "Parent content not found"},
    500: {"description": "Internal server error"}
}

COMMENT_UPDATE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Comment/Reply updated successfully"},
    403: {"description": "Forbidden"},
    404: {"description": "Comment/Reply not found"},
    500: {"description": "Internal server error"}
}

COMMENT_DELETE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Comment/Reply deleted successfully"},
    403: {"description": "Forbidden"},
    404: {"description": "Comment/Reply not found"},
    500: {"description": "Internal server error"}
}

# Like/Unlike Responses
LIKE_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Like/Unlike operation successful"},
    400: {"description": "Bad request"},
    404: {"description": "Blog not found"},
    500: {"description": "Internal server error"}
}

LIKE_STATUS_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    200: {"description": "Successfully retrieved like status"},
    404: {"description": "Blog not found"},
    500: {"description": "Internal server error"}
}
