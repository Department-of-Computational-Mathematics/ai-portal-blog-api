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
    200: {
        "description": "Service is healthy - all systems operational",
        "content": {
            "application/json": {
                "examples": {
                    "healthy": {
                        "summary": "All Services Healthy",
                        "value": {
                            "service": "blog-service",
                            "status": "healthy",
                            "timestamp": "2025-08-27T10:30:00Z",
                            "service_start_time": "2025-08-27T04:30:00+05:30",
                            "uptime_seconds": 21600.5,
                            "uptime_formatted": "6h 0m 0s",
                            "timezone": "GMT+5:30 (IST)",
                            "keycloak": {
                                "status": "healthy",
                                "response_time_ms": 150.25,
                                "service": "keycloak",
                                "authenticated": True
                            },
                            "database": {
                                "status": "healthy", 
                                "response_time_ms": 25.8,
                                "service": "mongodb",
                                "metrics": {
                                    "total_blogs": 42,
                                    "total_comments": 156,
                                    "total_replies": 89,
                                    "total_likes": 234,
                                    "total_content_items": 287
                                }
                            },
                            "overall_response_time_ms": 176.05
                        }
                    }
                }
            }
        }
    },
    503: {
        "description": "Service is degraded or unhealthy",
        "content": {
            "application/json": {
                "examples": {
                    "degraded": {
                        "summary": "Service Degraded - Partial Functionality",
                        "value": {
                            "service": "blog-service",
                            "status": "degraded",
                            "timestamp": "2025-08-27T10:30:00Z",
                            "service_start_time": "2025-08-27T04:30:00+05:30",
                            "uptime_seconds": 21600.5,
                            "uptime_formatted": "6h 0m 0s",
                            "timezone": "GMT+5:30 (IST)",
                            "keycloak": {
                                "status": "unhealthy",
                                "response_time_ms": None,
                                "service": "keycloak",
                                "authenticated": False,
                                "error": "Connection timeout"
                            },
                            "database": {
                                "status": "healthy",
                                "response_time_ms": 25.8,
                                "service": "mongodb",
                                "metrics": {
                                    "total_blogs": 42,
                                    "total_comments": 156,
                                    "total_replies": 89,
                                    "total_likes": 234,
                                    "total_content_items": 287
                                }
                            },
                            "overall_response_time_ms": 25.8
                        }
                    },
                    "unhealthy": {
                        "summary": "Service Unhealthy - Major Issues",
                        "value": {
                            "service": "blog-service",
                            "status": "unhealthy",
                            "timestamp": "2025-08-27T10:30:00Z",
                            "service_start_time": "2025-08-27T04:30:00+05:30",
                            "uptime_seconds": 21600.5,
                            "uptime_formatted": "6h 0m 0s",
                            "timezone": "GMT+5:30 (IST)",
                            "keycloak": {
                                "status": "unhealthy",
                                "response_time_ms": None,
                                "service": "keycloak",
                                "authenticated": False,
                                "error": "Service unavailable"
                            },
                            "database": {
                                "status": "unhealthy",
                                "response_time_ms": None,
                                "service": "mongodb",
                                "error": "Connection refused",
                                "metrics": None
                            },
                            "overall_response_time_ms": 0
                        }
                    }
                }
            }
        }
    }
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
