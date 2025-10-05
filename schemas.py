from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class Token(BaseModel):
    """Token model for authentication responses."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model for JWT payload."""
    email: Optional[str] = None

class UserBase(BaseModel):
    """Base user model with common user fields."""
    fullname: str
    email: Optional[EmailStr] = None  # Made optional
    phone: str  # Mandatory
    aadhar: Optional[str] = None  # Made optional
    dob: date
    pin: int
    role: Optional[str] = None
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        # Convert empty string to None for optional email
        if v == "" or v is None:
            return None
        return v
    
    @field_validator('aadhar', mode='before')
    @classmethod
    def validate_aadhar(cls, v):
        # Convert empty string to None for optional aadhar
        if v == "" or v is None:
            return None
        return v
    
    @field_validator('dob', mode='before')
    @classmethod
    def parse_dob(cls, value):
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return value
        
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
        }

class UserCreate(UserBase):
    """User creation model with optional password."""
    password: Optional[str] = None

class UserUpdate(BaseModel):
    """User update model with all optional fields."""
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    aadhar: Optional[str] = None
    dob: Optional[date] = None
    password: Optional[str] = None
    pin: Optional[int] = None
    role: Optional[str] = None

class User(UserBase):
    """User model with database ID."""
    user_id: int

    class Config:
        from_attributes = True

class UserCreateResponse(UserBase):
    """Response model for user creation with generated password."""
    user_id: int
    generated_password: Optional[str] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """User login model with multiple authentication options."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    aadhar: Optional[str] = None
    # password: Optional[str] = None
    # pin: Optional[str] = None
    
    @field_validator('email', 'phone', 'aadhar', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None"""
        if v == "" or v is None:
            return None
        return v

# Dynamic Table Schemas
class ColumnTypeEnum(str, Enum):
    """Enumeration of supported column types for dynamic tables."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TEXT = "text"
    JSON = "json"

class ColumnDefinitionBase(BaseModel):
    """Base model for column definitions in dynamic tables."""
    name: str
    description: Optional[str] = None
    column_type: ColumnTypeEnum
    is_required: bool = False
    is_unique: bool = False
    is_primary_key: bool = False
    is_index: bool = False
    default_value: Optional[str] = None
    max_length: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not isinstance(v, str) or not v.isidentifier():
            raise ValueError('Name must be a valid identifier (no spaces or special characters)')
        return v

class ColumnDefinitionCreate(ColumnDefinitionBase):
    """Model for creating new column definitions."""
    pass

class ColumnDefinition(ColumnDefinitionBase):
    """Complete column definition model with database fields."""
    id: int
    table_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TableDefinitionBase(BaseModel):
    """Base model for table definitions."""
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.isidentifier():
            raise ValueError('Table name must be a valid identifier (no spaces or special characters)')
        return v

class TableDefinitionCreate(TableDefinitionBase):
    """Model for creating new table definitions with columns."""
    columns: List[ColumnDefinitionCreate]

class TableDefinition(TableDefinitionBase):
    """Complete table definition model with database fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    columns: List[ColumnDefinition] = []

    class Config:
        from_attributes = True

class DynamicTableDataCreate(BaseModel):
    """Model for creating new data entries in dynamic tables."""
    data: Dict[str, Any]

class DynamicTableData(BaseModel):
    """Complete data entry model for dynamic tables."""
    id: int
    table_id: int
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

class DynamicTableQueryParams(BaseModel):
    """Query parameters for filtering and pagination of dynamic table data."""
    filter: Optional[Dict[str, Any]] = None
    sort: Optional[str] = None
    sort_dir: Optional[str] = "asc"
    page: Optional[int] = 1
    page_size: Optional[int] = 50

# Role schemas
class RoleBase(BaseModel):
    """Base model for user roles."""
    role_name: str
    role_code: str

class RoleCreate(RoleBase):
    """Model for creating new roles."""
    pass

class RoleUpdate(BaseModel):
    """Model for updating existing roles."""
    role_name: Optional[str] = None
    role_code: Optional[str] = None

class Role(RoleBase):
    """Complete role model with database ID."""
    role_id: int

    class Config:
        from_attributes = True    

# Login History schemas
class UserLoginHistoryBase(BaseModel):
    """Base model for user login history tracking."""
    user_id: int
    device_details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    login_status: Optional[str] = None

class UserLoginHistoryCreate(UserLoginHistoryBase):
    """Model for creating new login history entries."""
    pass

class UserLoginHistory(UserLoginHistoryBase):
    """Complete login history model with database fields."""
    user_login_id: int
    login_date: datetime

    class Config:
        from_attributes = True

# Interest Tracking schemas
class InterestTrackingBase(BaseModel):
    """Base model for interest tracking on chit funds."""
    user_id: int
    chit_id: int
    chit_no: int
    month: int
    year: int
    weeks_paid: int
    total_amount: int
    interest_rate: int = 1  # Default to 1%
    interest_amount: int

class InterestTrackingCreate(InterestTrackingBase):
    """Model for creating new interest tracking entries."""
    pass

class InterestTrackingUpdate(BaseModel):
    """Model for updating interest payment status."""
    is_paid: Optional[bool] = None
    paid_at: Optional[datetime] = None

class InterestTracking(InterestTrackingBase):
    """Complete interest tracking model with database fields."""
    interest_id: int
    calculated_at: datetime
    is_paid: bool
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChitUsers(BaseModel):
    """Chit User model with database ID."""
    chit_id: int
    user_id: int
    chit_no: int
    amount: int

    class Config:
        from_attributes = True  
