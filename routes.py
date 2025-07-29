from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from jose import JWTError, jwt

import crud
import schemas
import auth
from database import get_db
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    blacklist_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from utils import get_current_user_id

# Main router
router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to MyChitFund API"}

# Authentication router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.options("/cors-check")
async def cors_check():
    """
    Simple endpoint to check CORS configuration.
    This endpoint is used by the frontend to verify CORS is working correctly.
    """
    return {"status": "ok", "cors": "enabled"}

@auth_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Try to find user by email to get user_id for failed login record
        potential_user = crud.get_user_by_email(db, email=form_data.username)
        if potential_user:
            # Record failed login
            login_history = schemas.UserLoginHistoryCreate(
                user_id=potential_user.user_id,
                device_details={
                    "user_agent": request.headers.get("user-agent", ""),
                    "host": request.client.host if request.client else "unknown"
                },
                ip_address=request.client.host if request.client else None,
                login_status="failed"
            )
            crud.create_login_history(db, login_history)
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Record successful login
    login_history = schemas.UserLoginHistoryCreate(
        user_id=user.user_id,
        device_details={
            "user_agent": request.headers.get("user-agent", ""),
            "host": request.client.host if request.client else "unknown"
        },
        ip_address=request.client.host if request.client else None,
        login_status="success"
    )
    crud.create_login_history(db, login_history)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login", response_model=schemas.Token)
async def login(login_data: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    # Check if at least one identifier is provided
    if not login_data.email and not login_data.phone and not login_data.aadhar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of email, phone, or aadhar must be provided",
        )

    # Authenticate user by identifier without password
    user = auth.authenticate_user_by_identifier(
        db,
        email=login_data.email,
        phone=login_data.phone,
        aadhar=login_data.aadhar
    )

    if not user:
        # Record failed login attempt if email was provided
        if login_data.email:
            # Try to find user by email to get user_id
            potential_user = crud.get_user_by_email(db, email=login_data.email)
            if potential_user:
                # Record failed login
                login_history = schemas.UserLoginHistoryCreate(
                    user_id=potential_user.user_id,
                    device_details={
                        "user_agent": request.headers.get("user-agent", ""),
                        "host": request.client.host if request.client else "unknown"
                    },
                    ip_address=request.client.host if request.client else None,
                    login_status="failed"
                )
                crud.create_login_history(db, login_history)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found with provided credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Record successful login
    login_history = schemas.UserLoginHistoryCreate(
        user_id=user.user_id,
        device_details={
            "user_agent": request.headers.get("user-agent", ""),
            "host": request.client.host if request.client else "unknown"
        },
        ip_address=request.client.host if request.client else None,
        login_status="success"
    )
    crud.create_login_history(db, login_history)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=schemas.User)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

@auth_router.get("/validate-token")
async def validate_token(request: Request, db: Session = Depends(get_db)):
    """
    Validate a token without requiring authentication.
    This endpoint checks if a token is valid and not blacklisted.
    """
    # Get the authorization header
    authorization = request.headers.get("Authorization")
    
    # If no authorization header is provided, return invalid
    if not authorization:
        return {"valid": False, "message": "No token provided"}
    
    # Extract the token from the authorization header
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return {"valid": False, "message": "Invalid token format"}
    except ValueError:
        return {"valid": False, "message": "Invalid authorization header format"}
    
    # Check if the token is blacklisted
    if auth.is_token_blacklisted(token):
        return {"valid": False, "message": "Token is blacklisted"}
    
    # Validate the token
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return {"valid": False, "message": "Invalid token payload"}
        
        # Check if the user exists
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            return {"valid": False, "message": "User not found"}
        
        return {"valid": True, "message": "Token is valid"}
    except JWTError:
        return {"valid": False, "message": "Invalid token"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating token: {str(e)}"}

@auth_router.post("/refresh-token", response_model=schemas.Token)
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """
    Refresh an access token.
    This endpoint creates a new token with a new expiration time.
    """
    # Get the authorization header
    authorization = request.headers.get("Authorization")
    
    # If no authorization header is provided, return error
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the token from the authorization header
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if the token is blacklisted
    if auth.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate the token
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if the user exists
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create a new token with a new expiration time
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing token: {str(e)}",
        )

@auth_router.post("/logout")
async def logout(request: Request):
    """
    Logout endpoint to invalidate the current user's session.
    This endpoint will attempt to invalidate the token if provided.
    """
    # Get the authorization header
    authorization = request.headers.get("Authorization")
    
    # If no authorization header is provided, just return success
    # This allows clients to call logout even if they don't have a token
    if not authorization:
        return {"message": "Successfully logged out"}
    
    # Extract the token from the authorization header
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return {"message": "Successfully logged out"}
    except ValueError:
        return {"message": "Successfully logged out"}
    
    # Add the token to the blacklist if it exists
    if token:
        blacklist_token(token)
    
    # Note: The client should also remove the token from localStorage
    return {"message": "Successfully logged out"}

# Users router
users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@users_router.post("/", response_model=schemas.UserCreateResponse)
def create_user(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    # Check if email is provided and already exists
    if user.email:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@users_router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@users_router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, request: Request, db: Session = Depends(get_db), current_user_id: Optional[int] = Depends(get_current_user_id)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.update_user(db=db, user_id=user_id, user=user, current_user_id=current_user_id)

@users_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db=db, user_id=user_id)
    return {"message": "User deleted successfully"}


# Login History router
login_history_router = APIRouter(prefix="/login-history", tags=["Login History"])

@login_history_router.get("/", response_model=list[schemas.UserLoginHistory])
def read_all_login_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all login history entries"""
    return crud.get_all_login_history(db, skip=skip, limit=limit)

@login_history_router.get("/user/{user_id}", response_model=list[schemas.UserLoginHistory])
def read_user_login_history(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get login history for a specific user"""
    return crud.get_user_login_history(db, user_id=user_id, skip=skip, limit=limit)

@login_history_router.get("/{user_login_id}", response_model=schemas.UserLoginHistory)
def read_login_history(user_login_id: int, db: Session = Depends(get_db)):
    """Get a login history entry by ID"""
    login_history = crud.get_login_history(db, user_login_id=user_login_id)
    if login_history is None:
        raise HTTPException(status_code=404, detail="Login history entry not found")
    return login_history

# Roles router
roles_router = APIRouter(prefix="/roles", tags=["Roles"])

@roles_router.get("/", response_model=list[schemas.Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all roles"""
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles

@roles_router.post("/", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Create a new role"""
    return crud.create_role(db=db, role=role)

@roles_router.get("/{role_id}", response_model=schemas.Role)
def read_role(role_id: int, db: Session = Depends(get_db)):
    """Get a role by ID"""
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@roles_router.put("/{role_id}", response_model=schemas.Role)
def update_role(role_id: int, role: schemas.RoleUpdate, db: Session = Depends(get_db)):
    """Update a role"""
    return crud.update_role(db=db, role_id=role_id, role=role)

@roles_router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Delete a role"""
    return crud.delete_role(db=db, role_id=role_id)
