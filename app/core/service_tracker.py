"""
Service startup and uptime tracking module.
Tracks service start time in GMT+5:30 timezone and provides uptime calculation.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

# GMT+5:30 timezone (IST - Indian Standard Time)
IST = timezone(timedelta(hours=5, minutes=30))

# Global variable to store service start time
_service_start_time: Optional[datetime] = None


def initialize_service_start_time() -> datetime:
    """
    Initialize and record the service start time in IST timezone.
    This should be called once when the service starts.
    
    Returns:
        datetime: The service start time in IST timezone
    """
    global _service_start_time
    _service_start_time = datetime.now(IST)
    return _service_start_time


def get_service_start_time() -> Optional[datetime]:
    """
    Get the recorded service start time.
    
    Returns:
        Optional[datetime]: Service start time in IST timezone, None if not initialized
    """
    return _service_start_time


def get_uptime_seconds() -> Optional[float]:
    """
    Calculate the service uptime in seconds since startup.
    
    Returns:
        Optional[float]: Uptime in seconds, None if service start time is not recorded
    """
    if _service_start_time is None:
        return None
    
    current_time = datetime.now(IST)
    uptime_delta = current_time - _service_start_time
    return uptime_delta.total_seconds()


def get_uptime_info() -> dict:
    """
    Get comprehensive uptime information including formatted uptime string.
    
    Returns:
        dict: Dictionary containing uptime information
    """
    start_time = get_service_start_time()
    uptime_seconds = get_uptime_seconds()
    
    if start_time is None or uptime_seconds is None:
        return {
            "service_start_time": None,
            "uptime_seconds": None,
            "uptime_formatted": "Service start time not recorded",
            "timezone": "GMT+5:30 (IST)"
        }
    
    # Format uptime as human-readable string
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    uptime_parts = []
    if days > 0:
        uptime_parts.append(f"{days}d")
    if hours > 0:
        uptime_parts.append(f"{hours}h")
    if minutes > 0:
        uptime_parts.append(f"{minutes}m")
    uptime_parts.append(f"{seconds}s")
    
    uptime_formatted = " ".join(uptime_parts)
    
    return {
        "service_start_time": start_time.isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_formatted": uptime_formatted,
        "timezone": "GMT+5:30 (IST)",
        "current_time": datetime.now(IST).isoformat()
    }
