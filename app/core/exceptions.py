from fastapi import HTTPException, status
from typing import Optional, List

# ============================================================================
# Base Custom Exceptions
# ============================================================================

class BlogAPIException(HTTPException):
    """Base exception class for all blog API exceptions"""
    pass

# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================

class AuthenticationRequiredException(BlogAPIException):
    def __init__(self, detail: str = "User authentication required. X-User-ID header missing."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class KeycloakAuthenticationException(BlogAPIException):
    def __init__(self, detail: str = "Unauthorized access - invalid client or credentials for keycloak"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class KeycloakTokenException(BlogAPIException):
    def __init__(self, detail: str = "Unauthorized access - empty token received from Keycloak"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class PermissionDeniedException(BlogAPIException):
    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class BlogOwnershipException(BlogAPIException):
    def __init__(self, detail: str = "Permission denied. You can only edit your own blogs."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class CommentOwnershipException(BlogAPIException):
    def __init__(self, detail: str = "Permission denied. You can only edit your own comments."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class ReplyOwnershipException(BlogAPIException):
    def __init__(self, detail: str = "Permission denied. You can only edit your own replies."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

# ============================================================================
# Blog Related Exceptions
# ============================================================================

class BlogNotFoundException(BlogAPIException):
    def __init__(self, blog_id: Optional[str] = None):
        detail = f"Blog with id {blog_id} not found" if blog_id else "Blog not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class BlogInsertionException(BlogAPIException):
    def __init__(self, detail: str = "Blog Insertion failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class BlogUpdateException(BlogAPIException):
    def __init__(self, detail: str = "Blog update failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class BlogDeletionException(BlogAPIException):
    def __init__(self, detail: str = "Blog deletion failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class NoBlogsFoundException(BlogAPIException):
    def __init__(self, detail: str = "No blogs found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class BlogsByTagsNotFoundException(BlogAPIException):
    def __init__(self, tags: List[str] = []):
        detail = f"No blogs found with the given tags: {', '.join(tags)}" if tags else "No tags provided."
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

# ============================================================================
# Comment Related Exceptions
# ============================================================================

class CommentNotFoundException(BlogAPIException):
    def __init__(self, comment_id: Optional[str] = None):
        detail = f"Comment with id {comment_id} not found" if comment_id else "Comment not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class CommentInsertionException(BlogAPIException):
    def __init__(self, detail: str = "Comment Insertion failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class CommentUpdateException(BlogAPIException):
    def __init__(self, detail: str = "Comment update failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class CommentDeletionException(BlogAPIException):
    def __init__(self, detail: str = "Comment deletion failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class NoCommentsFoundException(BlogAPIException):
    def __init__(self, detail: str = "No comments found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class CommentOrReplyNotFoundException(BlogAPIException):
    def __init__(self, detail: str = "Comment or Reply not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

# ============================================================================
# Reply Related Exceptions
# ============================================================================

class ReplyNotFoundException(BlogAPIException):
    def __init__(self, reply_id: Optional[str] = None):
        detail = f"Reply with id {reply_id} not found" if reply_id else "Reply not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ReplyInsertionException(BlogAPIException):
    def __init__(self, detail: str = "Reply Insertion failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class ReplyUpdateException(BlogAPIException):
    def __init__(self, detail: str = "Reply update failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class ReplyDeletionException(BlogAPIException):
    def __init__(self, detail: str = "Reply deletion failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class ParentContentNotFoundException(BlogAPIException):
    def __init__(self, parent_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent content with id {parent_id} not found"
        )

# ============================================================================
# User Related Exceptions
# ============================================================================

class UserNotFoundException(BlogAPIException):
    def __init__(self, user_id: Optional[str] = None):
        detail = f"User not found with ID: {user_id}" if user_id else "User not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

# ============================================================================
# Like/Unlike Related Exceptions
# ============================================================================

class LikeUpdateException(BlogAPIException):
    def __init__(self, detail: str = "Like Update Failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class BlogLikeException(BlogAPIException):
    def __init__(self, detail: str = "Failed to like blog"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class BlogUnlikeException(BlogAPIException):
    def __init__(self, detail: str = "Failed to unlike blog"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class InvalidLikeValueException(BlogAPIException):
    def __init__(self, detail: str = "Invalid like value. Use 0 to unlike or 1 to like"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

# ============================================================================
# External Service Exceptions
# ============================================================================

class KeycloakServiceException(BlogAPIException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error. Keycloak returned a {status_code} - {detail} error"
        )

class KeycloakUserNotFoundException(BlogAPIException):
    def __init__(self, user_id: Optional[str] = None):
        detail = f"User not found in Keycloak with ID: {user_id}" if user_id else "User not found in Keycloak"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class DatabaseException(BlogAPIException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class InternalServerException(BlogAPIException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

# ============================================================================
# Validation Exceptions
# ============================================================================

class ValidationException(BlogAPIException):
    def __init__(self, detail: str = "Invalid input data"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class InvalidIdFormatException(BlogAPIException):
    def __init__(self, detail: str = "Invalid Id format"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
