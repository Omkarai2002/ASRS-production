from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import logging

from app.config import (
    DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_RECYCLE, 
    DB_CONNECT_TIMEOUT
)

logger = logging.getLogger(__name__)

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.getenv('rds_user')}:{os.getenv('rds_password')}@{os.getenv('rds_host')}:{os.getenv('rds_port', 3306)}/{os.getenv('rds_dbname')}"

# Create engine with optimized connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Test connection before use
    connect_args={
        'connect_timeout': DB_CONNECT_TIMEOUT,
        'charset': 'utf8mb4',
        'autocommit': False,
    },
    echo=False  # Set to True for SQL debugging
)

# Event listener to handle MySQL connection settings
@event.listens_for(engine, "connect")
def set_mysql_connection_settings(dbapi_conn, connection_record):
    """Set MySQL connection settings when connection is created"""
    try:
        cursor = dbapi_conn.cursor()
        cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES'")
        cursor.close()
    except Exception as e:
        logger.warning(f"Failed to set MySQL connection settings: {str(e)}")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)
Base = declarative_base()

# ==================== DATABASE UTILITIES ====================

def get_db_session() -> Session:
    """
    Get a database session with retry logic
    Attempts connection up to 3 times with delays
    """
    import time
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection
            db.execute(text("SELECT 1"))
            logger.debug(f"Database connection established (attempt {attempt + 1})")
            return db
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after max retries")
                raise

def close_db_session(db: Session):
    """Close database session safely"""
    try:
        if db:
            db.close()
    except Exception as e:
        logger.warning(f"Error closing database session: {str(e)}")

@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    Automatically handles connection and cleanup
    
    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = get_db_session()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise
    finally:
        close_db_session(db)

# ==================== DATABASE HEALTH CHECK ====================

def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database health check: OK")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


