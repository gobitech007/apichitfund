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
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

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
    details_id: int
    
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    user_id: int
    chit_no: int
    amount: int
    week_no: int
    pay_type: str  # card, UPI, netbanking
    
    # @validator('pay_type')
    def validate_pay_type(self, v):
        valid_types = ['card', 'UPI', 'netbanking']
        if v not in valid_types:
            raise ValueError(f'pay_type must be one of {valid_types}')
        return v

class PaymentCreate(PaymentBase):
    pay_card: Optional[str] = None  # credit/debit
    pay_card_name: Optional[str] = None
    pay_expiry_no: Optional[str] = None
    pay_qr: Optional[str] = None
    transaction_id: Optional[str] = None
    status: str  # completed/pending/failure
    
    # @validator('pay_card')
    def validate_pay_card(self, v, values):
        if values.get('pay_type') == 'card' and not v:
            raise ValueError('pay_card is required when pay_type is card')
        if v and v not in ['credit', 'debit']:
            raise ValueError('pay_card must be either credit or debit')
        return v
    
    # @validator('pay_card_name', 'pay_expiry_no')
    def validate_card_details(self, v, values):
        if values.get('pay_type') == 'card' and not v:
            field_name = 'pay_card_name' if v is None else 'pay_expiry_no'
            raise ValueError(f'{field_name} is required when pay_type is card')
        return v
    
    # @validator('pay_qr')
    def validate_upi_details(self, v, values):
        if values.get('pay_type') == 'UPI' and not v:
            raise ValueError('pay_qr is required when pay_type is UPI')
        return v

class PaymentResponse(PaymentBase):
    pay_id: int
    transaction_id: Optional[str] = None
    pay_card: Optional[str] = None
    pay_card_name: Optional[str] = None
    pay_expiry_no: Optional[str] = None
    pay_qr: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True

class TransactionHistoryResponse(BaseModel):
    chit_id: int
    user_id: int
    chit_no: int
    amount: Optional[int] = None
    week: int
    is_paid: str
    payment: Optional[PaymentResponse] = None
    
    class Config:
        from_attributes = True
