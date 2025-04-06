from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List

class UserBase(BaseModel):
    fullname: str
    email: EmailStr
    phone: str
    aadhar: str
    dob: date

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    aadhar: Optional[str] = None
    dob: Optional[date] = None
    password: Optional[str] = None

class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True

class UserCreateResponse(UserBase):
    user_id: int
    generated_password: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    aadhar: Optional[str] = None
