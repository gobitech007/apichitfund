from datetime import datetime, timedelta
import random
import string
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

# Define __all__ to explicitly export functions
__all__ = [
    'verify_password',
    'get_password_hash',
    'generate_random_password',
    'authenticate_user',
    'authenticate_user_by_identifier',
    'create_access_token',
    'get_current_user',
    'SECRET_KEY',
    'ALGORITHM',
    'ACCESS_TOKEN_EXPIRE_MINUTES'
]

# Security configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Password and authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_random_password(length=12):
    """Generate a secure random password with specified length"""
    # Include at least one of each: uppercase, lowercase, digit
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    # special = "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Ensure at least one of each type
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        # random.choice(special)
    ]

    # Fill the rest with random characters from all types
    all_chars = lowercase + uppercase + digits #+ special
    password.extend(random.choice(all_chars) for _ in range(length - 4))

    # Shuffle the password characters
    random.shuffle(password)

    return ''.join(password)

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def authenticate_user_by_identifier(db: Session, email: Optional[str] = None, phone: Optional[str] = None, aadhar: Optional[str] = None):
    """Authenticate user by email, phone, or aadhar without password"""
    user = None

    if email:
        user = crud.get_user_by_email(db, email)
    elif phone:
        user = crud.get_user_by_phone(db, phone)
    elif aadhar:
        user = crud.get_user_by_aadhar(db, aadhar)

    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user