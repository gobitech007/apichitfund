from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import InterestTracking
from schemas import InterestTracking as InterestTrackingSchema
from schemas import InterestTrackingCreate, InterestTrackingUpdate
from sqlalchemy import text

router = APIRouter(
    prefix="/interest",
    tags=["interest"],
    responses={404: {"description": "Not found"}},
)

@router.post("/calculate", response_model=List[InterestTrackingSchema])
def calculate_monthly_interest(month: int, year: int, db: Session = Depends(get_db)):
    """
    Calculate interest for a specific month and year using the stored procedure.
    """
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")
    
    try:
        # Call the stored procedure
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate interest: {str(e)}")

@router.get("/", response_model=List[InterestTrackingSchema])
def get_interest_records(
    month: Optional[int] = None,
    year: Optional[int] = None,
    user_id: Optional[int] = None,
    chit_id: Optional[int] = None,
    is_paid: Optional[bool] = None,
    db: Session = Depends(get_db)
):
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

@router.get("/{interest_id}", response_model=InterestTrackingSchema)
def get_interest_record(interest_id: int, db: Session = Depends(get_db)):
    """
    Get a specific interest record by ID.
    """
    interest_record = db.query(InterestTracking).filter(InterestTracking.interest_id == interest_id).first()
    
    if not interest_record:
        raise HTTPException(status_code=404, detail="Interest record not found")
    
    return interest_record

@router.patch("/{interest_id}", response_model=InterestTrackingSchema)
def update_interest_record(
    interest_id: int,
    interest_update: InterestTrackingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an interest record (mark as paid).
    """
    interest_record = db.query(InterestTracking).filter(InterestTracking.interest_id == interest_id).first()
    
    if not interest_record:
        raise HTTPException(status_code=404, detail="Interest record not found")
    
    # Update fields
    if interest_update.is_paid is not None:
        interest_record.is_paid = interest_update.is_paid
        
        # If marking as paid, set the paid_at timestamp
        if interest_update.is_paid:
            interest_record.paid_at = datetime.now()
    
    # If paid_at is explicitly provided, use it
    if interest_update.paid_at is not None:
        interest_record.paid_at = interest_update.paid_at
    
    db.commit()
    db.refresh(interest_record)
    
    return interest_record

@router.post("/{interest_id}/mark-paid", response_model=InterestTrackingSchema)
def mark_interest_as_paid(interest_id: int, db: Session = Depends(get_db)):
    """
    Mark an interest record as paid using the stored procedure.
    """
    try:
        # Call the stored procedure
        result = db.execute(text("CALL MarkInterestAsPaid(:interest_id)"), 
                           {"interest_id": interest_id})
        
        # Fetch the updated record
        updated_record = result.fetchone()
        
        if not updated_record:
            raise HTTPException(status_code=404, detail="Interest record not found")
        
        # Convert to dictionary
        interest_dict = {column: value for column, value in zip(result.keys(), updated_record)}
        
        return interest_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark interest as paid: {str(e)}")