"""
Status and debug service module.

This module contains services for:
- Health checks for various system components
- Debug utilities for header inspection
- System status monitoring
"""

import time
import os
import sys
from datetime import datetime
from typing import Dict, Any
from fastapi import Request
from app.schemas.blog import HealthCheckResponse, KeycloakHealth, DatabaseHealth
from app.services.keycloak import check_keycloak_health
from app.services.blog import check_database_health


async def get_comprehensive_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check for the blog service.
    
    Checks:
    - Keycloak authentication service connectivity and authentication capability
    - MongoDB database connectivity and performance metrics
    - Overall service response time and status
    
    Returns detailed health information including:
    - Individual service status and response times  
    - Database metrics (blog counts, comment counts, etc.)
    - Authentication status
    - Overall service health assessment
    """
    start_time = time.time()
    
    try:
        keycloak_health_raw = await check_keycloak_health()
        keycloak_health = KeycloakHealth(**keycloak_health_raw)
    except Exception as e:
        keycloak_health = KeycloakHealth(
            status="unhealthy",
            response_time_ms=None,
            service="keycloak", 
            authenticated=False,
            error=str(e)
        )
    
    try:
        database_health_raw = await check_database_health()
        database_health = DatabaseHealth(**database_health_raw)
    except Exception as e:
        database_health = DatabaseHealth(
            status="unhealthy",
            response_time_ms=None,
            service="mongodb",
            error=str(e),
            metrics=None
        )
    
    # Calculate overall response time
    overall_response_time = round((time.time() - start_time) * 1000, 2)
    
    # Determine overall health status
    keycloak_healthy = keycloak_health.status == "healthy"
    database_healthy = database_health.status == "healthy"
    
    if keycloak_healthy and database_healthy:
        overall_status = "healthy"
        status_code = 200
    elif database_healthy:  # Database is critical, if it's healthy but Keycloak isn't, we're degraded
        overall_status = "degraded"
        status_code = 503
    else:  # Database is unhealthy, service is unhealthy
        overall_status = "unhealthy"
        status_code = 503
    
    # Calculate uptime from actual service start time
    from app.core.service_tracker import get_uptime_info
    uptime_info = get_uptime_info()
    
    health_response = HealthCheckResponse(
        service="blog-service",
        status=overall_status,
        timestamp=datetime.utcnow(),
        service_start_time=uptime_info.get("service_start_time"),
        uptime_seconds=uptime_info.get("uptime_seconds"),
        uptime_formatted=uptime_info.get("uptime_formatted"),
        timezone=uptime_info.get("timezone", "GMT+5:30 (IST)"),
        keycloak=keycloak_health,
        database=database_health,
        overall_response_time_ms=overall_response_time
    )
    
    return {
        "health_response": health_response,
        "status_code": status_code
    }


async def get_request_headers_debug(request: Request) -> Dict[str, Any]:
    """
    Debug utility to inspect all incoming request headers.
    Useful for verifying nginx gateway is properly setting authentication headers.
    
    Args:
        request: FastAPI Request object containing headers
        
    Returns:
        Dictionary containing:
        - All headers
        - Important authentication-related headers highlighted
        - Header count and other metadata
    """
    headers = dict(request.headers)
    
    # Highlight important authentication-related headers
    auth_headers = {
        "x-user-id": headers.get("x-user-id"),
        "authorization": headers.get("authorization"),
        "x-forwarded-for": headers.get("x-forwarded-for"),
        "x-real-ip": headers.get("x-real-ip"),
        "x-forwarded-proto": headers.get("x-forwarded-proto"),
        "x-forwarded-host": headers.get("x-forwarded-host"),
        "host": headers.get("host"),
        "user-agent": headers.get("user-agent"),
    }
    
    # Remove None values for cleaner output
    auth_headers = {k: v for k, v in auth_headers.items() if v is not None}
    
    return {
        "message": "Request headers debug information",
        "timestamp": datetime.utcnow().isoformat(),
        "important_auth_headers": auth_headers,
        "all_headers": headers,
        "headers_count": len(headers),
        "nginx_headers_present": {
            "x_user_id_present": "x-user-id" in headers,
            "x_forwarded_for_present": "x-forwarded-for" in headers,
            "x_real_ip_present": "x-real-ip" in headers,
            "authorization_present": "authorization" in headers,
        }
    }


async def get_auth_debug_info(request: Request, current_user_id: str) -> Dict[str, Any]:
    """
    Debug utility to verify authentication flow and user ID extraction.
    
    Args:
        request: FastAPI Request object containing headers
        current_user_id: Processed user ID from the security dependency
        
    Returns:
        Dictionary containing:
        - Raw X-User-ID header value
        - Processed current_user_id from dependency
        - Header extraction success/failure
        - Authentication flow validation
    """
    raw_user_id_header = request.headers.get("x-user-id")
    auth_header = request.headers.get("authorization")
    
    # Additional debugging info
    debugging_info = {
        "header_case_variations": {
            "x-user-id": request.headers.get("x-user-id"),
            "X-User-ID": request.headers.get("X-User-ID"),
            "X-USER-ID": request.headers.get("X-USER-ID"),
        },
        "all_x_headers": {k: v for k, v in request.headers.items() if k.lower().startswith("x-")},
    }
    
    return {
        "message": "Authentication debug information",
        "timestamp": datetime.utcnow().isoformat(),
        "raw_x_user_id_header": raw_user_id_header,
        "processed_current_user_id": current_user_id,
        "authorization_header_present": auth_header is not None,
        "authorization_header_type": auth_header.split(" ")[0] if auth_header else None,
        "header_extraction_successful": raw_user_id_header is not None,
        "values_match": raw_user_id_header == current_user_id,
        "user_authenticated": current_user_id is not None,
        "nginx_gateway_working": raw_user_id_header is not None and current_user_id is not None,
        "debugging_info": debugging_info
    }


async def get_system_info() -> Dict[str, Any]:
    """
    Get general system information for debugging purposes.
    
    Returns:
        Dictionary containing system and environment information
    """
    from app.core.service_tracker import get_uptime_info
    
    uptime_info = get_uptime_info()
    
    return {
        "message": "System information",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "service_info": {
            "name": "blog-service",
            "version": os.getenv("SERVICE_VERSION", "unknown"),
            "uptime": uptime_info,
        },
        "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
        "python_version": sys.version,
    }


def is_debug_endpoint_enabled() -> bool:
    """
    Check if debug endpoints should be enabled based on environment.
    
    Returns:
        True if debug endpoints should be enabled, False otherwise
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    debug_enabled = os.getenv("DEBUG_ENDPOINTS_ENABLED", "true").lower() == "true"
    
    # Enable debug endpoints in development and staging, or if explicitly enabled
    return environment in ["development", "staging", "dev", "test"] or debug_enabled
