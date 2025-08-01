from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    fullname = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=True, unique=True, index=True)  # Made optional
    phone = Column(String(20), nullable=False, unique=True, index=True)  # Mandatory
    aadhar = Column(String(20), nullable=True, unique=False, index=False)  # Made optional
    dob = Column(Date, nullable=False)
    password = Column(String(100), nullable=False)
    pin = Column(Integer, nullable=True)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    # created_by = Column(String(100), ForeignKey("users.fullname", ondelete="SET NULL", name="fk_users_created_by", use_alter=True), nullable=True)
    # updated_by = Column(String(100), ForeignKey("users.fullname", ondelete="SET NULL", name="fk_users_updated_by", use_alter=True), nullable=True)
    
    
    # Self-referential relationships
    # created_by_user = relationship("User", foreign_keys=[created_by], remote_side=[user_id], backref="created_users")
    # updated_by_user = relationship("User", foreign_keys=[updated_by], remote_side=[user_id], backref="updated_users")

class ColumnType(enum.Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TEXT = "text"
    JSON = "json"

# class TableDefinition(Base):
#     __tablename__ = "table_definitions"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False, unique=True, index=True)
#     description = Column(String(255), nullable=True)
#     created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
#     # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
#     # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

#     # Relationships
#     columns = relationship("ColumnDefinition", back_populates="table", cascade="all, delete-orphan")
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[updated_by])

# class ColumnDefinition(Base):
#     __tablename__ = "column_definitions"

#     id = Column(Integer, primary_key=True, index=True)
#     table_id = Column(Integer, ForeignKey("table_definitions.id", ondelete="CASCADE"), nullable=False)
#     name = Column(String(100), nullable=False)
#     description = Column(String(255), nullable=True)
#     column_type = Column(String(50), nullable=False)  # Uses ColumnType enum values
#     is_required = Column(Boolean, default=False)
#     is_unique = Column(Boolean, default=False)
#     is_primary_key = Column(Boolean, default=False)
#     is_index = Column(Boolean, default=False)
#     default_value = Column(String(255), nullable=True)
#     max_length = Column(Integer, nullable=True)  # For string/text types
#     created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
#     # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
#     # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    
#     # Relationships
#     # creator = relationship("User", foreign_keys=[created_by])
#     # updater = relationship("User", foreign_keys=[updated_by])

#     # Relationships
#     table = relationship("TableDefinition", back_populates="columns")

#     __table_args__ = (
#         # Ensure column names are unique within a table
#         {'sqlite_autoincrement': True},
#     )

# class DynamicTableData(Base):
#     __tablename__ = "dynamic_table_data"

#     id = Column(Integer, primary_key=True, index=True)
#     table_id = Column(Integer, ForeignKey("table_definitions.id", ondelete="CASCADE"), nullable=False)
#     data = Column(JSON, nullable=False)  # Stores the row data as JSON
#     created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
#     # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
#     # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

#     # Relationships
#     table = relationship("TableDefinition")
#     # creator = relationship("User", foreign_keys=[created_by])
#     # updater = relationship("User", foreign_keys=[updated_by])

def create_tables(engine):
    """
    Create all tables in the database
    """
    Base.metadata.create_all(bind=engine)

class Chit_users(Base):
    __tablename__ = "chit_users"

    chit_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", name="fk_chit_users_user_id", use_alter=True))
    chit_no = Column(Integer)
    amount = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL", name="fk_chit_users_created_by", use_alter=True), nullable=True)
    # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL", name="fk_chit_users_updated_by", use_alter=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[updated_by])

class Pay_details(Base):
    __tablename__ = "pay_details"

    details_id = Column(Integer, primary_key=True, nullable=False, index=True)
    chit_id = Column(Integer, ForeignKey("chit_users.chit_id", name="fk_chit_users_chit_id", use_alter=True))
    week = Column(Integer, nullable=False)
    is_paid = Column(String(1), nullable=False)
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL", name="fk_chit_users_created_by", use_alter=True), nullable=True)
    # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL", name="fk_chit_users_updated_by", use_alter=True), nullable=True)
    
    # Relationships
    # chit_users = relationship("Chit_users", foreign_keys=[chit_id])
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[updated_by])

class Payment(Base):
    __tablename__ = "pay"

    pay_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", name="fk_payments_user_id", use_alter=True))
    chit_no = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    week_no = Column(Integer, nullable=False)
    pay_type = Column(String(20), nullable=False)  # card, UPI, netbanking
    pay_card = Column(String(20), nullable=True)   # credit/debit
    pay_card_name = Column(String(100), nullable=True)
    pay_expiry_no = Column(String(20), nullable=True)  # Changed from Integer to String
    pay_qr = Column(String(100), nullable=True)    # For UPI
    transaction_id = Column(String(50), nullable=True)  # Unique transaction ID
    status = Column(String(20), nullable=False)  # completed/pending/failure
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    created_by = Column(String(100), ForeignKey("users.fullname", ondelete="SET NULL", name="fk_payments_created_by", use_alter=True), nullable=True)
    updated_by = Column(String(100), ForeignKey("users.fullname", ondelete="SET NULL", name="fk_payments_updated_by", use_alter=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

class Role(Base):
    __tablename__ = "roles"
   
    role_id = Column(Integer, primary_key=True, nullable=False, index=True)
    role_name = Column(String(100), nullable=False, unique=True, index=True)
    role_code = Column(String(50), nullable=False, unique=True, index=True)
    # created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    # updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    
    # Relationships can be added here if needed, for example:
    # users = relationship("User", back_populates="role")

class UserLoginHistory(Base):
    __tablename__ = "user_login_history"
    
    user_login_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", name="fk_login_history_user_id", use_alter=True))
    login_date = Column(DateTime, server_default=func.now(), nullable=False)
    device_details = Column(JSON, nullable=True)  # Store device info as JSON
    ip_address = Column(String(50), nullable=True)
    login_status = Column(String(20), nullable=True)  # success, failed, etc.
    
    # Relationship to User
    user = relationship("User", foreign_keys=[user_id])
 

class InterestTracking(Base):
    __tablename__ = "interest_tracking"
    
    interest_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", name="fk_interest_user_id", use_alter=True))
    chit_id = Column(Integer, ForeignKey("chit_users.chit_id", name="fk_interest_chit_id", use_alter=True))
    chit_no = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    weeks_paid = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    interest_rate = Column(Integer, nullable=False, default=1)  # Stored as percentage (1 = 1%)
    interest_amount = Column(Integer, nullable=False)
    calculated_at = Column(DateTime, server_default=func.now())
    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    chit = relationship("Chit_users", foreign_keys=[chit_id])

