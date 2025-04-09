from fastapi import Request
from typing import Callable, Any
from jose import JWTError, jwt

from database import SessionLocal
from auth import SECRET_KEY, ALGORITHM
import crud


async def audit_middleware(request: Request, call_next: Callable) -> Any:
    """
    Middleware to add audit information to all database operations
    
    This middleware will be applied to all routes and will ensure that
    created_by and updated_by fields are populated for all database operations.
    """
    # Initialize user ID as None
    request.state.current_user_id = None
    
    # Only try to extract user ID for API routes, not for docs or static files
    path = request.url.path
    if path.startswith("/api/") and not path.startswith("/api/docs") and not path.startswith("/api/redoc"):
        # Try to get the current user ID from the token
        try:
            token = request.headers.get("Authorization", "")
            if token and token.startswith("Bearer "):
                token = token.replace("Bearer ", "")
                # Decode the token
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email = payload.get("sub")
                
                if email:
                    # Get a database session
                    db = SessionLocal()
                    try:
                        # Get the user by email
                        user = crud.get_user_by_email(db, email=email)
                        if user:
                            request.state.current_user_id = user.user_id
                    finally:
                        db.close()
        except (JWTError, Exception):
            # If any error occurs, just continue with current_user_id as None
            pass
    
    # Process the request
    response = await call_next(request)
    
    return response