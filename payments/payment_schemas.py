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

