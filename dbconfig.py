# dbconfig.py
import os

# Get the current environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "localhost")

# Database configuration based on environment
if ENVIRONMENT == "development":
    # Docker development environment
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:admin@db:3306/mychitfund"
    )
    PORT = 8001
else:
    # Local development environment
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:admin@localhost:3306/mychitfund"
    )
    PORT = 8000

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
if ENVIRONMENT == "development":
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
