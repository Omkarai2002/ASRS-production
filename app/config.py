"""
Configuration module for ASRS application
Centralized constants, configuration, and application settings
"""

import os
from enum import Enum
from typing import Dict, Tuple

# ==================== ENVIRONMENT ====================
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this-in-production")

# ==================== DATABASE ====================
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_RECYCLE = 3600  # 1 hour
DB_CONNECT_TIMEOUT = 10

# ==================== UPLOAD SETTINGS ====================
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
UPLOAD_DIR = "uploaded_reports"
EXCEL_EXPORT_TEMP_DIR = "temp/exports"
PDF_TEMP_DIR = "temp/pdfs"

# ==================== PAGINATION ====================
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ==================== EXCLUSION STATUSES ====================
class ExclusionStatus(str, Enum):
    FILLED = "Filled"
    EMPTY = "Empty Skid"
    STICKER_NOT_FOUND = "Sticker Not Found"
    MULTIPLE_STICKERS = "Multiple Stickers"
    OTHER = "Other"

EXCLUSION_STATUSES = [status.value for status in ExclusionStatus]

# ==================== COLOR MAPPING ====================
# Professional enterprise color palette
COLORS = {
    "primary": "#667eea",
    "primary_dark": "#764ba2",
    "secondary": "#f093fb",
    "secondary_light": "#f5576c",
    "success": "#34d399",
    "warning": "#fbbf24",
    "danger": "#f87171",
    "light": "#f3f4f6",
    "dark": "#1f2937",
    "border": "#e5e7eb",
    "text_primary": "#111827",
    "text_secondary": "#6b7280",
}

# Exclusion status to color mapping
EXCLUSION_COLOR_MAP = {
    ExclusionStatus.FILLED.value: COLORS["success"],
    ExclusionStatus.EMPTY.value: COLORS["warning"],
    ExclusionStatus.STICKER_NOT_FOUND.value: COLORS["danger"],
    ExclusionStatus.MULTIPLE_STICKERS.value: "#f97316",
    ExclusionStatus.OTHER.value: COLORS["text_secondary"],
}

# Exclusion status to background color mapping
EXCLUSION_BG_COLOR_MAP = {
    ExclusionStatus.FILLED.value: "rgba(52, 211, 153, 0.2)",
    ExclusionStatus.EMPTY.value: "rgba(251, 191, 36, 0.2)",
    ExclusionStatus.STICKER_NOT_FOUND.value: "rgba(236, 72, 153, 0.2)",
    ExclusionStatus.MULTIPLE_STICKERS.value: "rgba(249, 115, 22, 0.2)",
    ExclusionStatus.OTHER.value: "rgba(107, 114, 128, 0.2)",
}

# ==================== USER SETTINGS DEFAULTS ====================
DEFAULT_USER_SETTINGS = {
    "images_per_row": 5,
    "level_prefix": "L",
    "image_size": 200,  # pixels
    "show_image_info": True,
    "show_level_info": True,
}

# Images per row constraints
IMAGES_PER_ROW_MIN = 1
IMAGES_PER_ROW_MAX = 20

# ==================== SEARCH SETTINGS ====================
SEARCH_QUERY_MIN_LENGTH = 1
SEARCH_RESULTS_LIMIT = 500

# ==================== TIME SETTINGS ====================
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DASHBOARD_DAYS_WINDOW = 30  # Rolling window for dashboard stats

# ==================== API SETTINGS ====================
API_PREFIX = "/api"
API_RESPONSE_TIMEOUT = 30  # seconds

# ==================== PAGINATION DEFAULTS ====================
PAGINATION_DEFAULTS = {
    "page": 1,
    "page_size": 20,
}

# ==================== LOGGING ====================
LOG_LEVEL = "INFO" if not DEBUG else "DEBUG"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "asrs.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== AWS S3 ====================
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "asrs-bucket")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# ==================== WORKER SETTINGS ====================
UPLOAD_EXECUTOR_MAX_WORKERS = 4
UPLOAD_EXECUTOR_THREAD_PREFIX = "upload_worker_"

# ==================== DISPLAY SETTINGS ====================
ITEMS_PER_PAGE = 20
REPORTS_PER_PAGE = 10
SEARCH_RESULTS_PER_PAGE = 20

# ==================== QR CODE ====================
QR_CODE_SIZE = 4  # inches
QR_MODULE_DRAW_TYPE = "rect"
QR_BOX_SIZE = 10

# ==================== EXCEL EXPORT ====================
EXCEL_COLUMN_WIDTHS = {
    "A": 8,      # Item#
    "B": 12,     # Location
    "C": 20,     # Unique ID
    "D": 20,     # VIN
    "E": 10,     # Qty
    "F": 25,     # Image Name
    "G": 18,     # Exclusion
    "H": 18,     # Date
    "I": 15,     # Download
    "J": 15,     # Status
}

# ==================== VALIDATION RULES ====================
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

REPORT_NAME_MIN_LENGTH = 1
REPORT_NAME_MAX_LENGTH = 255

VIN_MIN_LENGTH = 1
VIN_MAX_LENGTH = 25

# ==================== FEATURE FLAGS ====================
ENABLE_BULK_QR_GENERATION = True
ENABLE_EXCEL_EXPORT = True
ENABLE_DASHBOARD_FILTERS = True
ENABLE_SEARCH_FEATURE = True
ENABLE_USER_SETTINGS = True

# ==================== SESSION SETTINGS ====================
SESSION_TIMEOUT_MINUTES = 60
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "lax"

# ==================== ERROR MESSAGES ====================
ERROR_MESSAGES = {
    "unauthorized": "You are not authorized to access this resource",
    "not_found": "The requested resource was not found",
    "invalid_input": "Invalid input provided",
    "database_error": "A database error occurred. Please try again later",
    "server_error": "An internal server error occurred",
    "file_too_large": f"File size exceeds maximum limit of {MAX_UPLOAD_SIZE / (1024*1024):.0f}MB",
    "invalid_file_type": f"Only these file types are allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
}

# ==================== SUCCESS MESSAGES ====================
SUCCESS_MESSAGES = {
    "upload_started": "File upload started. Please wait while we process your images",
    "upload_complete": "All images uploaded and processed successfully",
    "settings_saved": "Your settings have been saved successfully",
    "search_complete": "Search completed successfully",
    "export_complete": "Excel export completed successfully",
}

# Helper function to safely get configuration
def get_config(key: str, default=None):
    """Safe configuration getter"""
    return globals().get(key, default)
