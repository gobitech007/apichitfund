from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from database import engine
from models import create_tables
from routes import router, auth_router, users_router

# Create tables
create_tables(engine)

# FastAPI app
app = FastAPI(
    title="MyChitFund API",
    description="API for managing users in MyChitFund application",
    version="1.0.0",
    debug=True
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Include the API router in the main app
app.include_router(api_router)

# For running the application
if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://0.0.0.0:8000")
    print("API documentation available at http://localhost:8000/api/docs")
    print("API endpoints:")
    print("  GET    /api/            - Welcome message")
    print("  GET    /api/users/      - List all users")
    print("  POST   /api/users/      - Create a new user")
    print("  GET    /api/users/{user_id} - Get user by ID")
    print("  PUT    /api/users/{user_id} - Update user")
    print("  DELETE /api/users/{user_id} - Delete user")
    print("Authentication endpoints:")
    print("  POST   /api/auth/token  - Get access token (OAuth2 form)")
    print("  POST   /api/auth/login  - Login with email/password")
    print("  GET    /api/auth/me     - Get current user info")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")