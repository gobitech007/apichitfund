from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    fullname = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    aadhar = Column(String(20), nullable=False, unique=True, index=True)
    dob = Column(Date, nullable=False)
    password = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    
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

class TableDefinition(Base):
    __tablename__ = "table_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    columns = relationship("ColumnDefinition", back_populates="table", cascade="all, delete-orphan")
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[updated_by])

class ColumnDefinition(Base):
    __tablename__ = "column_definitions"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_definitions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    column_type = Column(String(50), nullable=False)  # Uses ColumnType enum values
    is_required = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)
    is_primary_key = Column(Boolean, default=False)
    is_index = Column(Boolean, default=False)
    default_value = Column(String(255), nullable=True)
    max_length = Column(Integer, nullable=True)  # For string/text types
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[updated_by])

    # Relationships
    table = relationship("TableDefinition", back_populates="columns")

    __table_args__ = (
        # Ensure column names are unique within a table
        {'sqlite_autoincrement': True},
    )

class DynamicTableData(Base):
    __tablename__ = "dynamic_table_data"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_definitions.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSON, nullable=False)  # Stores the row data as JSON
    created_at = Column(DateTime, server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # pylint: disable=E1102
    # created_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    # updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    table = relationship("TableDefinition")
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[updated_by])

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


