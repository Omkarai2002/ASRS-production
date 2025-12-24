"""
Logging configuration for ASRS application
Structured logging with file rotation and console output
"""

import logging
import logging.handlers
import os
from app.config import LOG_LEVEL, LOG_DIR, LOG_FILE, LOG_FORMAT, ENV

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Define formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

simple_formatter = logging.Formatter(
    '%(levelname)s - %(message)s'
)

# Root logger configuration
root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)

# Remove default handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(detailed_formatter)
file_handler.setLevel(logging.INFO)
root_logger.addHandler(file_handler)

# Console handler for development
console_handler = logging.StreamHandler()
console_handler.setFormatter(simple_formatter if ENV == "production" else detailed_formatter)
console_handler.setLevel(logging.INFO)
root_logger.addHandler(console_handler)

# Application logger
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a module-specific logger"""
    return logging.getLogger(name)
