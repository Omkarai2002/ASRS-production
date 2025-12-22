from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.getenv('rds_user')}:{os.getenv('rds_password')}@{os.getenv('rds_host')}:{os.getenv('rds_port', 3306)}/{os.getenv('rds_dbname')}"

# Create engine with connection pooling and better timeout handling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Number of connections to create beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Test connection before using it
    connect_args={
        'connect_timeout': 10,  # Connection timeout in seconds
        'charset': 'utf8mb4',
        'autocommit': False,
    },
    echo=False  # Set to True for SQL debugging
)

# Event listener to handle stale connections
@event.listens_for(engine, "connect")
def set_mysql_connection_settings(dbapi_conn, connection_record):
    """Set MySQL connection settings when connection is created"""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES'")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

