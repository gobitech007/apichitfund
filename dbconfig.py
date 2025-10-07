# dbconfig.py
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the current environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "localhost")
logger.info(f"Environment detected: {ENVIRONMENT}")

# Database configuration based on environment
if ENVIRONMENT == "development":
    # Docker development environment
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:admin@db:3306/mychitfund"
    )
    PORT = int(os.getenv("PORT", "8001"))
    logger.info(f"Using Docker development configuration (PORT: {PORT})")
else:
    # Local development environment
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:admin@db:3306/mychitfund"
    )
    PORT = int(os.getenv("PORT", "8000"))
    logger.info(f"Using local development configuration (PORT: {PORT})")

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
if ENVIRONMENT == "development":
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

logger.info(f"Database URL configured (host extracted): {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'unknown'}")
