from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from database import engine
from models import create_tables
from routes import router, auth_router, users_router, roles_router, login_history_router, chits_router
from payments.payments_routes import payments_router
from interest.interest_routes import router as interest_router
# from dynamic_tables_routes import dynamic_tables_router
from middleware import audit_middleware
from migrations import run_migrations

# Create tables and run migrations
create_tables(engine)
run_migrations()

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
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:54113", "http://smchitfund.local:3001", "http://smchitfund.local:3000", "http://smchitfund.local", "http://www.smchitfund.local"],  # React app origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Type"]
)

# Add audit middleware
@app.middleware("http")
async def audit_middleware_wrapper(request: Request, call_next):
    return await audit_middleware(request, call_next)

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
# api_router.include_router(dynamic_tables_router)

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
    print("  POST   /api/auth/token         - Get access token (OAuth2 form)")
    print("  POST   /api/auth/login         - Login with email/phone number")
    print("  GET    /api/auth/me            - Get current user info")
    print("  POST   /api/auth/logout        - Logout and invalidate session")
    print("  GET    /api/auth/validate-token - Check if a token is valid")
    print("Roles endpoints:")
    print("  GET    /api/roles/      - List all roles")
    print("  POST   /api/roles/      - Create a new role")
    print("  GET    /api/roles/{role_id} - Get role by ID")
    print("  PUT    /api/roles/{role_id} - Update role")
    print("  DELETE /api/roles/{role_id} - Delete role")
    print("Login History endpoints:")
    print("  GET    /api/login-history/ - List all login history entries")
    print("  GET    /api/login-history/user/{user_id} - List login history for a specific user")
    print("  GET    /api/login-history/{user_login_id} - Get login history entry by ID")
    print(" GET /api/chits/ - List all chits")
    # print("Dynamic Tables endpoints:")
    # print("  POST   /api/tables/     - Create a new table definition")
    # print("  GET    /api/tables/     - List all table definitions")
    # print("  GET    /api/tables/{table_id} - Get table definition by ID")
    # print("  PUT    /api/tables/{table_id} - Update table definition")
    # print("  DELETE /api/tables/{table_id} - Delete table definition")
    # print("  POST   /api/tables/{table_id}/columns - Add a column to a table")
    # print("  GET    /api/tables/{table_id}/columns - List all columns in a table")
    # print("  POST   /api/tables/{table_id}/data - Add a row of data to a table")
    # print("  GET    /api/tables/{table_id}/data - List all rows in a table")
    print("Payments endpoints:")
    print("  GET    /api/payments/chits/ - List all chits")
    print("  GET    /api/payments/chits/user/{user_id} - List all chits for a specific user")
    print("  POST   /api/payments/chit_users/ - Create a new chit user association")
    print("  PATCH  /api/payments/chits/{user_id} - Update amount for a specific chit")
    print("  GET    /api/payments/transaction-history/ - Get transaction history with optional user_id and chit_no filters")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")