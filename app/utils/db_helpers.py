"""Database helper utilities with retry logic for connection issues"""

from backend.database import SessionLocal
from sqlalchemy.exc import OperationalError
import time
import logging

logger = logging.getLogger(__name__)

def get_db_with_retry(max_retries=3, retry_delay=1):
    """
    Get a database session with retry logic for connection failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        Database session or None if all retries fail
    """
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection
            db.execute("SELECT 1")
            return db
        except OperationalError as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise
    
    return None


def execute_query_with_retry(query_func, max_retries=3, retry_delay=1):
    """
    Execute a database query function with retry logic.
    
    Args:
        query_func: Function that executes the query and returns result
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        Query result or raises exception if all retries fail
    """
    for attempt in range(max_retries):
        try:
            return query_func()
        except OperationalError as e:
            logger.warning(f"Query attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"Query failed after {max_retries} attempts")
                raise
