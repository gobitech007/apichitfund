from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class ChitSchemaBase(BaseModel):
    chit_no: int
    user_id: int
    amount: Optional[int] = None

class ChitUserCreate(BaseModel):
    user_id: int
    chit_no: int
    amount: Optional[int] = None

class ChitUserResponse(ChitSchemaBase):
    chit_id: int

    class Config:
        from_attributes = True

class ChitUserUpdate(BaseModel):
    amount: int

    class Config:
        from_attributes = True

class PaymentSchema(ChitSchemaBase):
    pay_id: int

class PayDetailBase(BaseModel):
    chit_id: int
    week: int
    is_paid: str

    # @validator('week')
    def validate_week(self, v):
        if not 1 <= v <= 54:
            raise ValueError('Week must be between 1 and 54')
        return v

    # @validator('is_paid')
    def validate_is_paid(self, v):
        if v not in ['Y', 'N']:
            raise ValueError('is_paid must be either Y or N')
        return v

class PayDetailCreate(PayDetailBase):
    pass

class PayDetailResponse(PayDetailBase):
    id: int

    class Config:
        orm_mode = True
