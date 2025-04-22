from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime

from models import InterestTracking
from schemas import InterestTrackingCreate

class InterestService:
    @staticmethod
    def calculate_monthly_interest(db: Session, month: int, year: int) -> List[Dict[str, Any]]:
        """
        Calculate interest for a specific month and year using the stored procedure.
        """
        result = db.execute(text("CALL CalculateMonthlyInterest(:month, :year)"), 
                           {"month": month, "year": year})
        
        # Fetch all rows from the result
        interest_records = result.fetchall()
        
        # Convert to list of dictionaries
        interest_list = []
        for record in interest_records:
            interest_dict = {column: value for column, value in zip(result.keys(), record)}
            interest_list.append(interest_dict)
        
        return interest_list
    
    @staticmethod
    def get_interest_records(
        db: Session,
        month: Optional[int] = None,
        year: Optional[int] = None,
        user_id: Optional[int] = None,
        chit_id: Optional[int] = None,
        is_paid: Optional[bool] = None
    ) -> List[InterestTracking]:
        """
        Get interest records with optional filtering.
        """
        query = db.query(InterestTracking)
        
        if month is not None:
            query = query.filter(InterestTracking.month == month)
        
        if year is not None:
            query = query.filter(InterestTracking.year == year)
        
        if user_id is not None:
            query = query.filter(InterestTracking.user_id == user_id)
        
        if chit_id is not None:
            query = query.filter(InterestTracking.chit_id == chit_id)
        
        if is_paid is not None:
            query = query.filter(InterestTracking.is_paid == is_paid)
        
        return query.all()
    
    @staticmethod
    def get_interest_record_by_id(db: Session, interest_id: int) -> Optional[InterestTracking]:
        """
        Get a specific interest record by ID.
        """
        return db.query(InterestTracking).filter(InterestTracking.interest_id == interest_id).first()
    
    @staticmethod
    def mark_interest_as_paid(db: Session, interest_id: int) -> Dict[str, Any]:
        """
        Mark an interest record as paid using the stored procedure.
        """
        result = db.execute(text("CALL MarkInterestAsPaid(:interest_id)"), 
                           {"interest_id": interest_id})
        
        # Fetch the updated record
        updated_record = result.fetchone()
        
        # Convert to dictionary
        if updated_record:
            interest_dict = {column: value for column, value in zip(result.keys(), updated_record)}
            return interest_dict
        
        return None
    
    @staticmethod
    def create_interest_record(db: Session, interest_data: InterestTrackingCreate) -> InterestTracking:
        """
        Create a new interest record manually.
        """
        interest_record = InterestTracking(
            user_id=interest_data.user_id,
            chit_id=interest_data.chit_id,
            chit_no=interest_data.chit_no,
            month=interest_data.month,
            year=interest_data.year,
            weeks_paid=interest_data.weeks_paid,
            total_amount=interest_data.total_amount,
            interest_rate=interest_data.interest_rate,
            interest_amount=interest_data.interest_amount,
            calculated_at=datetime.now(),
            is_paid=False
        )
        
        db.add(interest_record)
        db.commit()
        db.refresh(interest_record)
        
        return interest_record
    
    @staticmethod
    def update_interest_record(
        db: Session, 
        interest_id: int, 
        is_paid: Optional[bool] = None,
        paid_at: Optional[datetime] = None
    ) -> Optional[InterestTracking]:
        """
        Update an interest record (mark as paid).
        """
        interest_record = db.query(InterestTracking).filter(InterestTracking.interest_id == interest_id).first()
        
        if not interest_record:
            return None
        
        # Update fields
        if is_paid is not None:
            interest_record.is_paid = is_paid
            
            # If marking as paid, set the paid_at timestamp
            if is_paid and not interest_record.paid_at:
                interest_record.paid_at = datetime.now()
        
        # If paid_at is explicitly provided, use it
        if paid_at is not None:
            interest_record.paid_at = paid_at
        
        db.commit()
        db.refresh(interest_record)
        
        return interest_record