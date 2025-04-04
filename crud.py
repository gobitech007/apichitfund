from sqlalchemy.orm import Session
from fastapi import HTTPException, status

import models
import schemas
import auth

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_aadhar(db: Session, aadhar: str):
    return db.query(models.User).filter(models.User.aadhar == aadhar).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
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

    # Return the generated password if one was created
    result = db_user
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

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
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

    db.commit()
    db.refresh(db_user)
    return db_user

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