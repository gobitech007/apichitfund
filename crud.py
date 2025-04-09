from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

import models
import schemas
import auth
from payments import payment_schemas
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
    
    try:
        # Try to create with all fields including audit fields
        db_user = models.User(
            fullname=user.fullname,
            email=user.email,
            phone=user.phone,
            aadhar=user.aadhar,
            dob=user.dob,
            password=hashed_password
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
    create_chit_user(db, payment_schemas.ChitUserCreate(user_id=db_user.user_id, chit_no=1), current_user_id)
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
            "generated_password": generated_password
        }

    return result

def update_user(db: Session, user_id: int, user: schemas.UserUpdate, current_user_id: int = None):
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

def get_chit_by_user_id_and_chit_no(db: Session, user_id: int, chit_no: int):
    return db.query(models.Chit_users).filter(
        models.Chit_users.user_id == user_id,
        models.Chit_users.chit_no == chit_no
    ).first()

def update_chit_amount(db: Session, user_id: int, chit_no: int, base_amount: int, current_user_id: int = None):
    db_chit = get_chit_by_user_id_and_chit_no(db, user_id=user_id, chit_no=chit_no)
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
            db_chit = get_chit_by_user_id_and_chit_no(db, user_id=user_id, chit_no=chit_no)
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
    # Create new pay_details
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
    
def get_pay_details(db: Session, chit_id: int) -> List[models.Pay_details]:
    return db.query(models.Pay_details).filter(models.Pay_details.chit_id == chit_id).all()

def update_pay_detail(db: Session, chit_id: int, week: int, is_paid: str) -> models.Pay_details:
    pay_detail = db.query(models.Pay_details).filter(
        models.Pay_details.chit_id == chit_id,
        models.Pay_details.week == week
    ).first()
    
    if pay_detail:
        pay_detail.is_paid = is_paid
        db.commit()
        db.refresh(pay_detail)
    return pay_detail
