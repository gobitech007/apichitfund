# database.py
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logger = logging.getLogger(__name__)

# Log the database URL (mask password for security)
# logger.info(f"Connecting to database: {masked_url}")

# Create engine with connection pooling and timeout handling
engine = create_engine(
    "mysql+pymysql://root:admin@db:3306/mychitfund",
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour (3600 seconds)
    pool_size=10,        # Maximum number of connections to keep open
    max_overflow=20,     # Maximum number of connections that can be created beyond pool_size
    connect_args={
        "connect_timeout": 60,  # Connection timeout in seconds
        "read_timeout": 60,     # Read timeout in seconds
        "write_timeout": 60     # Write timeout in seconds
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
