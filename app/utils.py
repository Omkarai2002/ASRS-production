"""
Utility functions for ASRS application
Shared functions used across routers and services
"""

from functools import wraps
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
import logging

from app.config import (
    DATE_FORMAT, DATETIME_FORMAT, DEFAULT_USER_SETTINGS,
    ERROR_MESSAGES, EXCLUSION_COLOR_MAP
)

logger = logging.getLogger(__name__)

# ==================== SESSION & AUTH ====================
def get_user_id_from_session(request: Request) -> Optional[int]:
    """Extract user_id from session safely"""
    try:
        return request.session.get("user_id")
    except Exception as e:
        logger.warning(f"Failed to get user_id from session: {str(e)}")
        return None

def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user_id = get_user_id_from_session(request)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        return await func(request, *args, **kwargs)
    return wrapper

def check_user_auth(request: Request) -> tuple[bool, Optional[int]]:
    """Check if user is authenticated. Returns (is_auth, user_id)"""
    user_id = get_user_id_from_session(request)
    return (user_id is not None, user_id)

# ==================== DATETIME FORMATTING ====================
def format_date(date_obj: Optional[datetime], format: str = DATE_FORMAT) -> str:
    """Format datetime object to string safely"""
    if not date_obj:
        return "N/A"
    try:
        return date_obj.strftime(format)
    except Exception as e:
        logger.warning(f"Failed to format date: {str(e)}")
        return "N/A"

def format_datetime(date_obj: Optional[datetime]) -> str:
    """Format datetime with time component"""
    return format_date(date_obj, DATETIME_FORMAT)

def get_date_only(date_obj: Optional[datetime]) -> str:
    """Get date part only (YYYY-MM-DD)"""
    return format_date(date_obj, DATE_FORMAT)

# ==================== LOCATION CALCULATION ====================
def calculate_location(index: int, images_per_row: int, level_prefix: str = "L") -> str:
    """
    Calculate grid location for an item
    Returns format: L1-1, L1-2, L2-1, etc.
    """
    level_number = (index // images_per_row) + 1
    position_in_level = (index % images_per_row) + 1
    return f"{level_prefix}{level_number}-{position_in_level}"

def get_location_parts(index: int, images_per_row: int) -> Dict[str, int]:
    """Get level and position as dict"""
    return {
        "level": (index // images_per_row) + 1,
        "position": (index % images_per_row) + 1,
    }

# ==================== RESPONSE FORMATTING ====================
def success_response(data: Any = None, message: str = None, status_code: int = 200) -> JSONResponse:
    """Standard success response format"""
    response = {
        "status": "success",
        "data": data,
    }
    if message:
        response["message"] = message
    return JSONResponse(response, status_code=status_code)

def error_response(error: str, status_code: int = 400, details: Dict = None) -> JSONResponse:
    """Standard error response format"""
    response = {
        "status": "error",
        "error": error,
    }
    if details:
        response["details"] = details
    return JSONResponse(response, status_code=status_code)

def paginated_response(items: List, total: int, page: int, page_size: int) -> Dict:
    """Standard paginated response format"""
    total_pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }
    }

# ==================== ERROR HANDLING ====================
def get_error_message(error_key: str, custom_msg: str = None) -> str:
    """Get error message from predefined messages"""
    return custom_msg or ERROR_MESSAGES.get(error_key, "An error occurred")

def format_error_for_response(exception: Exception, error_key: str = "server_error") -> tuple[str, int]:
    """Format exception for API response. Returns (message, status_code)"""
    logger.error(f"Exception occurred: {str(exception)}", exc_info=True)
    
    if "unauthorized" in str(exception).lower():
        return (ERROR_MESSAGES.get("unauthorized"), 401)
    elif "not found" in str(exception).lower():
        return (ERROR_MESSAGES.get("not_found"), 404)
    else:
        return (ERROR_MESSAGES.get(error_key), 500)

# ==================== COLOR & STYLING ====================
def get_exclusion_color(exclusion_status: str) -> str:
    """Get color for exclusion status"""
    return EXCLUSION_COLOR_MAP.get(exclusion_status, "#95a5a6")

def get_exclusion_badge_class(exclusion_status: str) -> str:
    """Get CSS class name for exclusion badge"""
    if not exclusion_status:
        return "other"
    
    mapping = {
        "Filled": "filled",
        "Empty Skid": "empty",
        "Sticker Not Found": "sticker-not-found",
        "Multiple Stickers": "multiple",
    }
    return mapping.get(exclusion_status, "other")

# ==================== VALIDATION ====================
def validate_string(value: str, min_len: int = 1, max_len: int = 255, 
                   allow_empty: bool = False) -> tuple[bool, str]:
    """
    Validate string input
    Returns (is_valid, error_message)
    """
    if not value:
        if allow_empty:
            return (True, "")
        return (False, f"This field cannot be empty")
    
    value_stripped = value.strip()
    if len(value_stripped) < min_len:
        return (False, f"Minimum {min_len} characters required")
    
    if len(value_stripped) > max_len:
        return (False, f"Maximum {max_len} characters allowed")
    
    return (True, "")

def validate_file_extension(filename: str, allowed_extensions: set) -> tuple[bool, str]:
    """
    Validate file extension
    Returns (is_valid, error_message)
    """
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        return (False, f"Invalid file type: {ext}. Allowed types: {', '.join(allowed_extensions)}")
    return (True, "")

def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename"""
    import re
    # Allow alphanumeric, underscore, dash, dot
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

# ==================== DATA TRANSFORMATION ====================
def dict_from_db_model(obj, exclude: List[str] = None) -> Dict:
    """Convert SQLAlchemy model to dict"""
    if not obj:
        return {}
    
    result = {}
    for key, value in obj.__dict__.items():
        if key.startswith('_'):
            continue
        if exclude and key in exclude:
            continue
        
        if isinstance(value, datetime):
            result[key] = format_datetime(value)
        else:
            result[key] = value
    
    return result

def list_from_db_models(models, exclude: List[str] = None) -> List[Dict]:
    """Convert list of SQLAlchemy models to list of dicts"""
    return [dict_from_db_model(m, exclude) for m in models]

# ==================== USER SETTINGS ====================
def get_user_display_settings(user_settings) -> Dict:
    """Extract display settings from UserSettings object"""
    if not user_settings:
        return DEFAULT_USER_SETTINGS.copy()
    
    return {
        "images_per_row": user_settings.images_per_row or DEFAULT_USER_SETTINGS["images_per_row"],
        "level_prefix": user_settings.level_prefix or DEFAULT_USER_SETTINGS["level_prefix"],
        "image_size": user_settings.image_size or DEFAULT_USER_SETTINGS["image_size"],
        "show_image_info": user_settings.show_image_info,
        "show_level_info": user_settings.show_level_info,
    }

# ==================== LOGGING ====================
def log_action(user_id: int, action: str, details: Dict = None):
    """Log user action for audit trail"""
    msg = f"User {user_id}: {action}"
    if details:
        msg += f" | {details}"
    logger.info(msg)

def log_error(user_id: int, error: str, details: Dict = None):
    """Log error with user context"""
    msg = f"User {user_id} ERROR: {error}"
    if details:
        msg += f" | {details}"
    logger.error(msg)

# ==================== SEARCH ====================
def normalize_search_query(query: str) -> str:
    """Normalize search query for database matching"""
    return query.strip().replace(" ", "%")

# ==================== BATCH OPERATIONS ====================
def batch_items(items: List, batch_size: int = 100) -> List[List]:
    """Split list into batches"""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches
