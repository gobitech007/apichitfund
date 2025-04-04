from sqlalchemy import Column, Integer, String, Date
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    fullname = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    aadhar = Column(String(20), nullable=False, unique=True, index=True)
    dob = Column(Date, nullable=False)

def create_tables(engine):
    """
    Create all tables in the database
    """
    Base.metadata.create_all(bind=engine)
