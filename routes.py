from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from payments import payment_schemas

import crud
import schemas
import auth
from database import get_db
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login", response_model=schemas.Token)
async def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found with provided credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=schemas.User)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

# Users router
users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@users_router.post("/", response_model=schemas.UserCreateResponse)
def create_user(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db), current_user_id: Optional[int] = Depends(get_current_user_id)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user, current_user_id=current_user_id)

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

# Payments router
payments_router = APIRouter(prefix="/payments", tags=["Payments"])

@payments_router.get("/chits/", response_model=list[payment_schemas.ChitSchemaBase])
def chit_list_read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    chit_list = crud.get_chit_list(db, skip=skip, limit=limit)
    return chit_list

@payments_router.get("/chits/user/{user_id}", response_model=list[payment_schemas.ChitSchemaBase])
def get_user_chits(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Get chits for the user
    chits = crud.get_chits_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    if not chits:
        raise HTTPException(status_code=404, detail="No chits found for this user")

    return chits

@payments_router.post("/chit_users/", response_model=payment_schemas.ChitUserResponse)
def create_chit_user(chit_user: payment_schemas.ChitUserCreate, request: Request, db: Session = Depends(get_db), current_user_id: Optional[int] = Depends(get_current_user_id)):
    return crud.create_chit_user(db=db, chit_user=chit_user, current_user_id=current_user_id)

@payments_router.patch("/chits/user/{user_id}/chit/{chit_no}", response_model=payment_schemas.ChitUserResponse)
def update_chit_amount(user_id: int, chit_no: int, chit_update: payment_schemas.ChitUserUpdate, request: Request, db: Session = Depends(get_db), current_user_id: Optional[int] = Depends(get_current_user_id)):
    return crud.update_chit_amount(db=db, user_id=user_id, chit_no=chit_no, base_amount=chit_update.amount, current_user_id=current_user_id)
