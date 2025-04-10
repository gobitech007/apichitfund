from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class UserBase(BaseModel):
    fullname: str
    email: EmailStr
    phone: str
    aadhar: str
    dob: date
    pin: int
    role: Optional[str] = None
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
        }
        
    @validator('dob', pre=True)
    def parse_dob(cls, value):
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return value

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    aadhar: Optional[str] = None
    dob: Optional[date] = None
    password: Optional[str] = None
    pin: Optional[int] = None
    role: Optional[str] = None

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

# Dynamic Table Schemas
class ColumnTypeEnum(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TEXT = "text"
    JSON = "json"

class ColumnDefinitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    column_type: ColumnTypeEnum
    is_required: bool = False
    is_unique: bool = False
    is_primary_key: bool = False
    is_index: bool = False
    default_value: Optional[str] = None
    max_length: Optional[int] = None

    # @validator('name')
    def validate_name(self, v): # Added 'self' as the first argument
        if not isinstance(v, str) or not v.isidentifier():
            raise ValueError('Name must be a valid identifier (no spaces or special characters)')
        return v

class ColumnDefinitionCreate(ColumnDefinitionBase):
    pass

class ColumnDefinition(ColumnDefinitionBase):
    id: int
    table_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TableDefinitionBase(BaseModel):
    name: str
    description: Optional[str] = None

    # @validator('name')
    def validate_name(self, v):
        if not v.isidentifier():
            raise ValueError('Table name must be a valid identifier (no spaces or special characters)')
        return v

class TableDefinitionCreate(TableDefinitionBase):
    columns: List[ColumnDefinitionCreate]

class TableDefinition(TableDefinitionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    columns: List[ColumnDefinition] = []

    class Config:
        from_attributes = True

class DynamicTableDataCreate(BaseModel):
    data: Dict[str, Any]

class DynamicTableData(BaseModel):
    id: int
    table_id: int
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

class DynamicTableQueryParams(BaseModel):
    filter: Optional[Dict[str, Any]] = None
    sort: Optional[str] = None
    sort_dir: Optional[str] = "asc"
    page: Optional[int] = 1
    page_size: Optional[int] = 50

# Role schemas
class RoleBase(BaseModel):
    role_name: str
    role_code: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    role_code: Optional[str] = None

class Role(RoleBase):
    role_id: int

    class Config:
        from_attributes = True    
