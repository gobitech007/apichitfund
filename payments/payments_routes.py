from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from typing import Optional
from payments import payment_schemas

import crud
import models
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
    
    try:
        # Create pay details
        pay_details = crud.create_pay_details(db=db, chit_id=chit_id)
        return pay_details
    except HTTPException as e:
        # Re-raise the HTTP exception from the CRUD function
        raise e
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating pay details: {str(e)}"
        )

@payments_router.get("/chit_users/{chit_id}/pay_details/",response_model=List[payment_schemas.PayDetailResponse])
def read_pay_details(chit_id: int,db: Session = Depends(get_db), current_user_id: Optional[int] = Depends(get_current_user_id)):
    pay_details = crud.get_pay_details(db=db, chit_id=chit_id)
    if not pay_details:
        raise HTTPException(status_code=404, detail="Pay details not found")
    return pay_details

@payments_router.patch("/chit_users/{chit_id}/pay_details/{week}", response_model=payment_schemas.PayDetailResponse)
def update_pay_detail_status(chit_id: int, week: int, is_paid: str, db: Session = Depends(get_db), current_user_id: Optional[int] = Depends(get_current_user_id)):
    if not 1 <= week <= 54:
        raise HTTPException(status_code=400, detail="Week must be between 1 and 54")
    if is_paid not in ['Y', 'N']:
        raise HTTPException(status_code=400, detail="is_paid must be either Y or N")
    
    # First check if the pay detail exists and get its current status
    existing_pay_detail = db.query(models.Pay_details).filter(
        models.Pay_details.chit_id == chit_id,
        models.Pay_details.week == week
    ).first()
    
    if not existing_pay_detail:
        raise HTTPException(status_code=404, detail="Pay detail not found")
    
    # If it's already paid and we're trying to mark it as paid again, return a message
    if existing_pay_detail.is_paid == 'Y' and is_paid == 'Y':
        return existing_pay_detail  # Return the existing record without changes
    
    # Otherwise, update the pay detail
    pay_detail = crud.update_pay_detail(db=db, chit_id=chit_id, week=week, is_paid=is_paid)
    return pay_detail

# Payment processing endpoints
@payments_router.post("/process/", response_model=payment_schemas.PaymentResponse)
def create_payment(
    payment: payment_schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id)
):
    """
    Process a new payment with the following details:
    - user_id: ID of the user making the payment
    - chit_no: Chit number
    - amount: Payment amount
    - week_no: Week number for the payment
    - pay_type: Payment type (card, UPI, netbanking)
    
    For card payments, also include:
    - pay_card: Card type (credit/debit)
    - pay_card_name: Name on the card
    - pay_expiry_no: Card expiry date
    
    For UPI payments, also include:
    - pay_qr: UPI QR code or ID
    """
    # Validate payment data based on payment type
    if payment.pay_type == 'card':
        if not payment.pay_card or not payment.pay_card_name or not payment.pay_expiry_no:
            raise HTTPException(
                status_code=400, 
                detail="Card payments require pay_card, pay_card_name, and pay_expiry_no"
            )
    elif payment.pay_type == 'UPI':
        if not payment.pay_qr:
            raise HTTPException(
                status_code=400, 
                detail="UPI payments require pay_qr"
            )
        # For UPI payments, explicitly set card-related fields to None
        payment.pay_card = None
        payment.pay_card_name = None
        payment.pay_expiry_no = None
    
    # Create the payment
    return crud.create_payment(db=db, payment=payment, current_user_id=current_user_id)

@payments_router.get("/", response_model=List[payment_schemas.PaymentResponse])
def read_payments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id)
):
    """Get all payments"""
    payments = crud.get_payments(db=db, skip=skip, limit=limit)
    return payments

@payments_router.get("/{pay_id}", response_model=payment_schemas.PaymentResponse)
def read_payment(
    pay_id: int,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id)
):
    """Get a specific payment by ID"""
    payment = crud.get_payment(db=db, pay_id=pay_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@payments_router.get("/user/{user_id}", response_model=List[payment_schemas.PaymentResponse])
def read_user_payments(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id)
):
    """Get all payments for a specific user"""
    # Check if user exists
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    payments = crud.get_user_payments(db=db, user_id=user_id, skip=skip, limit=limit)
    return payments
