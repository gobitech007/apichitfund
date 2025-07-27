from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

import models
import schemas
import auth
from payments import payment_schemas
import random
import time
# from audit import add_audit_fields

def get_user(db: Session, user_id: int):
    """ return db.query(models.User).filter(models.User.user_id == user_id).first() """    
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """ return db.query(models.User).filter(models.User.email == email).first() """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_aadhar(db: Session, aadhar: str):
    return db.query(models.User).filter(models.User.aadhar == aadhar).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, current_user_id: int = None):
    # Check if user with same email exists
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if user with same aadhar exists
    if get_user_by_aadhar(db, aadhar=user.aadhar):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aadhar already registered"
        )

    # Check if user with same phone exists
    if get_user_by_phone(db, phone=user.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    # Generate a random password if none is provided
    generated_password = None
    if user.password is None:
        generated_password = auth.generate_random_password()
        password = generated_password
    else:
        password = user.password

    # Create new user with hashed password
    hashed_password = auth.get_password_hash(password)
    if user.role is None:
        user.role = "customer"
    
    try:
        # Try to create with all fields including audit fields
        db_user = models.User(
            fullname=user.fullname,
            email=user.email,
            phone=user.phone,
            aadhar=user.aadhar,
            dob=user.dob,
            password=hashed_password,
            pin= user.pin,
            role= user.role
        )
        
        # Add audit fields
        # add_audit_fields(db_user, current_user_id, is_new=True)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        # If there's an error, try again with just the basic fields
        db.rollback()
        
        if "unknown column" in str(e).lower() or "no such column" in str(e).lower():
            # Create with just the basic fields
            db_user = models.User(
                fullname=user.fullname,
                email=user.email,
                phone=user.phone,
                aadhar=user.aadhar,
                dob=user.dob,
                password=hashed_password
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            # If it's some other error, re-raise it
            raise

    # Return the generated password if one was created
    result = db_user
    create_chit_user(db, payment_schemas.ChitUserCreate(user_id=db_user.user_id, chit_no=1))
    if generated_password:
        # We need to convert the ORM model to a dict and add the password
        # We can't modify the SQLAlchemy model directly
        result = {
            "user_id": db_user.user_id,
            "fullname": db_user.fullname,
            "email": db_user.email,
            "phone": db_user.phone,
            "aadhar": db_user.aadhar,
            "dob": db_user.dob,
            "generated_password": generated_password,
            "pin": db_user.pin,
            "role": db_user.role
        }

    return result

def update_user(db: Session, user_id: int, user: schemas.UserUpdate, current_user_id: str = None):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields if provided
    user_data = user.dict(exclude_unset=True)

    # Handle password update separately
    if "password" in user_data:
        password = auth.get_password_hash(user_data["password"])
        user_data["password"] = password

    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    try:
        # Add audit fields
        # add_audit_fields(db_user, current_user_id, is_new=False)
        if current_user_id:
            db_user["updated_by"] = current_user_id

        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        # If there's an error updating with audit fields, try again without them
        db.rollback()
        
        if "unknown column" in str(e).lower() or "no such column" in str(e).lower():
            # Get a fresh copy of the user
            db_user = get_user(db, user_id)
            
            # Update fields again
            for key, value in user_data.items():
                setattr(db_user, key, value)
            
            db.commit()
            db.refresh(db_user)
            return db_user
        else:
            # If it's some other error, re-raise it
            raise

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

#chit_payment
def get_chit_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Chit_users).offset(skip).limit(limit).all()

def get_chits_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Chit_users).filter(models.Chit_users.user_id == user_id).offset(skip).limit(limit).all()

def get_chit_by_id(db: Session, chit_id: int):
    return db.query(models.Chit_users).filter(models.Chit_users.chit_id == chit_id).first()

def get_chit_by_user_id_and_chit_no(db: Session, user_id: int, amount: int):
    return db.query(models.Chit_users).filter(
        models.Chit_users.user_id == user_id,
        models.Chit_users.amount == amount
    ).first()

def update_chit_amount(db: Session, user_id: int, amount: int, base_amount: int, current_user_id: int = None):
    db_chit = get_chit_by_user_id_and_chit_no(db, user_id=user_id, amount=amount)
    if not db_chit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chit not found for this user and chit number"
        )

    db_chit.amount = base_amount
    
    try:
        # Add audit fields
        # add_audit_fields(db_chit, current_user_id, is_new=False)
        
        db.commit()
        db.refresh(db_chit)
        return db_chit
    except Exception as e:
        # If there's an error updating with audit fields, try again without them
        db.rollback()
        
        if "unknown column" in str(e).lower() or "no such column" in str(e).lower():
            # Just update the amount without audit fields
            db_chit = get_chit_by_user_id_and_chit_no(db, user_id=user_id, amount=amount)
            db_chit.amount = base_amount
            
            db.commit()
            db.refresh(db_chit)
            return db_chit
        else:
            # If it's some other error, re-raise it
            raise

def create_chit_user(db: Session, chit_user: "payment_schemas.ChitUserCreate", current_user_id: int = None):
    # Check if user exists
    db_user = get_user(db, user_id=chit_user.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if a chit with the same user_id and chit_no already exists
    existing_chit = get_chit_by_user_id_and_chit_no(db, user_id=chit_user.user_id, amount=chit_user.amount)
    if existing_chit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chit with amount {chit_user.amount} already exists for {db_user.fullname}"
        )

    # Create new chit_user
    try:
        # Try to create with all fields including audit fields
        db_chit_user = models.Chit_users(
            user_id=chit_user.user_id,
            chit_no=chit_user.chit_no,
            amount=chit_user.amount
        )
        
        # Add audit fields
        # add_audit_fields(db_chit_user, chit_user.user_id, is_new=True)
        
        db.add(db_chit_user)
        db.commit()
        db.refresh(db_chit_user)
        # ... existing fields ...
        # pay_details = relationship("pay_details", back_populates="chit")
        create_pay_details(db, db_chit_user.chit_id)
        return db_chit_user
    except Exception as e:
        # If there's an error, try again with just the basic fields
        # This is a fallback for when the database schema hasn't been updated yet
        db.rollback()
        
        if "unknown column" in str(e).lower() or "no such column" in str(e).lower():
            # Create with just the basic fields
            db_chit_user = models.Chit_users(
                user_id=chit_user.user_id,
                chit_no=chit_user.chit_no,
                amount=chit_user.amount
            )
            
            db.add(db_chit_user)
            db.commit()
            db.refresh(db_chit_user)
            
            return db_chit_user
        else:
            # If it's some other error, re-raise it
            raise

def create_pay_details(db: Session, chit_id: int = None):
    # Check if pay_details already exist for this chit_id
    existing_pay_details = db.query(models.Pay_details).filter(
        models.Pay_details.chit_id == chit_id
    ).first()
    
    if existing_pay_details:
        # Pay details already exist for this chit_id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pay details already exist for chit_id {chit_id}"
        )
    
    # Create new pay_details
    try:
        # Try to create with all fields including audit fields
        pay_details = []
        for week in range(1, 55):
            db_pay_details = models.Pay_details(
                chit_id=chit_id,
                week=week,
                is_paid='N'
            )
            db.add(db_pay_details)  # Add each instance individually
            pay_details.append(db_pay_details)
        
        # Add audit fields
        # add_audit_fields(db_pay_details, current_user_id, is_new=True)
        
        db.commit()
        # Refresh each instance individually
        for db_pay_details in pay_details:
            db.refresh(db_pay_details)
    
        return pay_details
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating pay details: {str(e)}"
        ) from e
    
def get_pay_details(db: Session, chit_id: int) -> List[models.Pay_details]:
    return db.query(models.Pay_details).filter(models.Pay_details.chit_id == chit_id).all()

def update_pay_detail(db: Session, chit_id: int, week: int, is_paid: str) -> models.Pay_details:
    pay_detail = db.query(models.Pay_details).filter(
        models.Pay_details.chit_id == chit_id,
        models.Pay_details.week == week
    ).first()
    
    if not pay_detail:
        return None
    
    # If the pay detail is already marked as paid (Y) and we're trying to update it,
    # return the current pay detail without making changes
    if pay_detail.is_paid == 'Y' and is_paid == 'Y':
        # No need to update, it's already paid
        return pay_detail
    
    # If we're changing from paid (Y) to unpaid (N), we should allow this for corrections
    # Or if we're changing from unpaid (N) to paid (Y), we should also allow this
    pay_detail.is_paid = is_paid
    db.commit()
    db.refresh(pay_detail)
    return pay_detail

def create_payment(db: Session, payment: "payment_schemas.PaymentCreate", current_user_id: int = None):
    """Create a new payment record"""
    # Check if user exists
    db_user = get_user(db, user_id=payment.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate a random transaction ID if not provided    
    # Use the provided transaction_id or generate a new one
    transaction_id = payment.transaction_id
    if not transaction_id:
        # Generate a unique transaction ID: timestamp + random number
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        transaction_id = f"TXN{timestamp}{random_num}"
    
    # Create new payment
    try:
        db_payment = models.Payment(
            user_id=payment.user_id,
            chit_no=payment.chit_no,
            amount=payment.amount,
            week_no=payment.week_no,
            pay_type=payment.pay_type,
            pay_card=payment.pay_card,
            pay_card_name=payment.pay_card_name,
            pay_expiry_no=payment.pay_expiry_no,
            pay_qr=payment.pay_qr,
            transaction_id=transaction_id,
            status="completed",  # Set a default status
            created_by=current_user_id
        )
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        # Update the pay_details to mark the week as paid
        # Find the chit_id based on user_id and chit_no
        chit_user = db.query(models.Chit_users).filter(
            models.Chit_users.user_id == payment.user_id,
            models.Chit_users.chit_no == payment.chit_no
        ).first()
        
        if chit_user:
            # Update the chit user's amount if needed
            if payment.amount and (chit_user.amount is None or chit_user.amount != payment.amount):
                chit_user.amount = payment.amount
                db.commit()
                db.refresh(chit_user)
            
            # Update the pay_detail for this week
            pay_detail = db.query(models.Pay_details).filter(
                models.Pay_details.chit_id == chit_user.chit_id,
                models.Pay_details.week == payment.week_no
            ).first()
            
            if pay_detail and pay_detail.is_paid == 'N':
                pay_detail.is_paid = 'Y'
                db.commit()
                db.refresh(pay_detail)
            else:
                # If pay_detail doesn't exist for some reason, create it
                new_pay_detail = models.Pay_details(
                    chit_id=chit_user.chit_id,
                    week=payment.week_no,
                    is_paid='Y'
                )
                db.add(new_pay_detail)
                db.commit()
                db.refresh(new_pay_detail)
        else:
            # If chit_user doesn't exist, create it
            new_chit_user = models.Chit_users(
                user_id=payment.user_id,
                chit_no=payment.chit_no,
                amount=payment.amount
            )
            db.add(new_chit_user)
            db.commit()
            db.refresh(new_chit_user)
            
            # Create pay_detail for this week
            new_pay_detail = models.Pay_details(
                chit_id=new_chit_user.chit_id,
                week=payment.week_no,
                is_paid='Y'
            )
            db.add(new_pay_detail)
            db.commit()
            db.refresh(new_pay_detail)
        
        # Add transaction_id to the payment response
        db_payment.transaction_id = transaction_id
        return db_payment
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment: {str(e)}"
        ) from e

def get_payments(db: Session, skip: int = 0, limit: int = 100):
    """Get all payments"""
    return db.query(models.Payment).offset(skip).limit(limit).all()

def get_payment(db: Session, pay_id: int):
    """Get a specific payment by ID"""
    return db.query(models.Payment).filter(models.Payment.pay_id == pay_id).first()

def get_payments_by_transaction_id(db: Session, transaction_id: str):
    """Get all payments with the same transaction ID prefix"""
    # Use LIKE query to match transaction IDs with the same prefix
    # This handles cases where transaction_id is in format "TXN12345-W1", "TXN12345-W2", etc.
    base_transaction_id = transaction_id.split('-')[0]
    return db.query(models.Payment).filter(
        models.Payment.transaction_id.like(f"{base_transaction_id}%")
    ).all()

def get_user_payments(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all payments for a specific user"""
    return db.query(models.Payment).filter(models.Payment.user_id == user_id).offset(skip).limit(limit).all()

# Role CRUD operations
def get_role(db: Session, role_id: int):
    """Get a role by ID"""
    return db.query(models.Role).filter(models.Role.role_id == role_id).first()

def get_role_by_code(db: Session, role_code: str):
    """Get a role by code"""
    return db.query(models.Role).filter(models.Role.role_code == role_code).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    """Get all roles"""
    return db.query(models.Role).offset(skip).limit(limit).all()

def create_role(db: Session, role: schemas.RoleCreate):
    """Create a new role"""
    # Check if role with same code exists
    if get_role_by_code(db, role_code=role.role_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role code already exists"
        )
    
    # Create new role
    db_role = models.Role(
        role_name=role.role_name,
        role_code=role.role_code
    )
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: int, role: schemas.RoleUpdate):
    """Update an existing role"""
    db_role = get_role(db, role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Update role fields if provided
    role_data = role.dict(exclude_unset=True)
    
    # If role_code is being updated, check if it already exists
    if "role_code" in role_data and role_data["role_code"] != db_role.role_code:
        if get_role_by_code(db, role_code=role_data["role_code"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role code already exists"
            )
    
    for key, value in role_data.items():
        setattr(db_role, key, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    """Delete a role"""
    db_role = get_role(db, role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    db.delete(db_role)
    db.commit()
    return {"message": "Role deleted successfully"}

# Login History CRUD operations
def create_login_history(db: Session, login_history: schemas.UserLoginHistoryCreate):
    """Create a new login history entry"""
    db_login_history = models.UserLoginHistory(
        user_id=login_history.user_id,
        device_details=login_history.device_details,
        ip_address=login_history.ip_address,
        login_status=login_history.login_status
    )
    db.add(db_login_history)
    db.commit()
    db.refresh(db_login_history)
    return db_login_history

def get_login_history(db: Session, user_login_id: int):
    """Get a login history entry by ID"""
    return db.query(models.UserLoginHistory).filter(models.UserLoginHistory.user_login_id == user_login_id).first()

def get_user_login_history(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get login history for a specific user"""
    return db.query(models.UserLoginHistory).filter(
        models.UserLoginHistory.user_id == user_id
    ).order_by(models.UserLoginHistory.login_date.desc()).offset(skip).limit(limit).all()

def get_all_login_history(db: Session, skip: int = 0, limit: int = 100):
    """Get all login history entries"""
    return db.query(models.UserLoginHistory).order_by(
        models.UserLoginHistory.login_date.desc()
    ).offset(skip).limit(limit).all()

def get_transaction_history(db: Session, user_id: int = None, chit_no: int = None, skip: int = 0, limit: int = 100):
    """
    Get transaction history combining data from chit_users, pay_details, and pay tables
    
    Args:
        db: Database session
        user_id: Optional filter by user ID
        chit_no: Optional filter by chit number
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of transaction history records
    """
    try:
        # Start with a query that joins chit_users and pay_details
        query = db.query(
            models.Chit_users,
            models.Pay_details,
            models.Payment
        ).join(
            models.Pay_details,
            models.Chit_users.chit_id == models.Pay_details.chit_id
        ).outerjoin(  # Use outer join to include weeks without payments
            models.Payment,
            (models.Chit_users.user_id == models.Payment.user_id) &
            (models.Chit_users.chit_no == models.Payment.chit_no) &
            (models.Pay_details.week == models.Payment.week_no)
        )
        
        # Apply filters if provided
        if user_id:
            query = query.filter(models.Chit_users.user_id == user_id)
        
        if chit_no:
            query = query.filter(models.Chit_users.chit_no == chit_no)
        
        # Order by user_id, chit_no, and week for consistent results
        query = query.order_by(
            models.Chit_users.user_id,
            models.Chit_users.chit_no,
            models.Pay_details.week
        )
        
        # Apply pagination
        results = query.offset(skip).limit(limit).all()
        
        # Convert the results to a list of dictionaries
        transaction_history = []
        for row in results:
            chit_user, pay_detail, payment = row
            
            # Create a dictionary for this transaction
            transaction = {
                "chit_id": chit_user.chit_id,
                "user_id": chit_user.user_id,
                "chit_no": chit_user.chit_no,
                "amount": chit_user.amount,
                "week": pay_detail.week,
                "is_paid": pay_detail.is_paid,
                "payment": None
            }
            
            # Only include payment if it exists
            if payment:
                transaction["payment"] = {
                    "pay_id": payment.pay_id,
                    "user_id": payment.user_id,
                    "chit_no": payment.chit_no,
                    "amount": payment.amount,
                    "week_no": payment.week_no,
                    "pay_type": payment.pay_type,
                    "pay_card": payment.pay_card,
                    "pay_card_name": payment.pay_card_name,
                    "pay_expiry_no": payment.pay_expiry_no,
                    "pay_qr": payment.pay_qr,
                    "transaction_id": payment.transaction_id,
                    "status": payment.status,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None
                }
            
            transaction_history.append(transaction)
        
        return transaction_history
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_transaction_history: {str(e)}")
        # Re-raise the exception to be handled by the API endpoint
        raise
