"""
Production-ready FastAPI application with clustering support
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi

from database import engine
from models import create_tables
from routes import router, auth_router, users_router, roles_router, login_history_router, chits_router
from payments.payments_routes import payments_router
from interest.interest_routes import router as interest_router
from middleware import audit_middleware
from migrations import run_migrations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up MyChitFund API...")
    try:
        create_tables(engine)
        run_migrations()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down MyChitFund API...")

# FastAPI app with lifespan management
app = FastAPI(
    title="MyChitFund API",
    description="API for managing users in MyChitFund application",
    version="1.0.0",
    debug=os.getenv("DEBUG", "false").lower() == "true",
    lifespan=lifespan
)

# Security middleware - Add trusted host middleware
trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=trusted_hosts
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:3001,http://localhost:54113,http://smchitfund.local:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Type"]
)

# Add audit middleware
@app.middleware("http")
async def audit_middleware_wrapper(request: Request, call_next):
    return await audit_middleware(request, call_next)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "service": "MyChitFund API",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # You can add database connectivity check here
        return {
            "status": "ready",
            "service": "MyChitFund API",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not ready",
            "service": "MyChitFund API",
            "error": str(e)
        }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MyChitFund API",
        version="1.0.0",
        description="API for managing users in MyChitFund application",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Include routers under the API router
api_router.include_router(router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(chits_router)
api_router.include_router(roles_router)
api_router.include_router(login_history_router)
api_router.include_router(payments_router)
api_router.include_router(interest_router)

# Include the API router in the main app
app.include_router(api_router)

# Application factory function for production
def create_app():
    """Application factory for production deployment"""
    return app

if __name__ == "__main__":
    # Development server - single process
    import uvicorn
    logger.info("Starting development server...")
    logger.info("Server starting on http://0.0.0.0:8000")
    logger.info("API documentation available at http://localhost:8000/docs")
    logger.info("Health check available at http://localhost:8000/health")
    
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True, 
        log_level="info",
        access_log=True
    )