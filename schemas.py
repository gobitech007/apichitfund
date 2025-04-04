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
    id: int

    class Config:
        orm_mode = True

class UserCreateResponse(User):
    generated_password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
