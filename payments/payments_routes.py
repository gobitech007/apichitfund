from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from typing import Optional
from payments import payment_schemas

import crud
from database import get_db
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from utils import get_current_user_id
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

# Add these new endpoints to your existing payments_router

@payments_router.post("/chit_users/{chit_id}/pay_details/", 
                     response_model=List[payment_schemas.PayDetailBase])
def create_pay_details(
    chit_id: int,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id)
):
    # Verify chit exists and belongs to user
    chit_user = crud.get_chit_by_id(db, chit_id=chit_id)
    if not chit_user:
        raise HTTPException(status_code=404, detail="Chit not found")
    
    # Create pay details
    pay_details = crud.create_pay_details(db=db,pay_details=payment_schemas.PayDetailBase, chit_id=chit_id)
    return pay_details

@payments_router.get("/chit_users/{chit_id}/pay_details/", 
                    response_model=List[payment_schemas.PayDetailResponse])
def read_pay_details(
    chit_id: int,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id)
):
    pay_details = crud.get_pay_details(db=db, chit_id=chit_id)
    if not pay_details:
        raise HTTPException(status_code=404, detail="Pay details not found")
    return pay_details

@payments_router.patch("/chit_users/{chit_id}/pay_details/{week}", 
                      response_model=payment_schemas.PayDetailResponse)
def update_pay_detail_status(
    chit_id: int,
    week: int,
    is_paid: str,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id)
):
    if not 1 <= week <= 54:
        raise HTTPException(status_code=400, detail="Week must be between 1 and 54")
    if is_paid not in ['Y', 'N']:
        raise HTTPException(status_code=400, detail="is_paid must be either Y or N")
    
    pay_detail = crud.update_pay_detail(db=db, chit_id=chit_id, week=week, is_paid=is_paid)
    if not pay_detail:
        raise HTTPException(status_code=404, detail="Pay detail not found")
    return pay_detail
