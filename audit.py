from typing import Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from fastapi import Depends, Request

from auth import get_current_user
from database import get_db
import models


def add_audit_fields(db_obj: Any, current_user_id: Optional[int] = None, is_new: bool = True) -> None:
    """
    Add audit fields (created_by, updated_by) to a database object
    
    Args:
        db_obj: The database object to update
        current_user_id: The ID of the current user (if available)
        is_new: Whether this is a new object (True) or an update (False)
    """
    try:
        if hasattr(db_obj, 'updated_by') and current_user_id is not None:
            setattr(db_obj, 'updated_by', current_user_id)
            
        if is_new and hasattr(db_obj, 'created_by') and current_user_id is not None:
            setattr(db_obj, 'created_by', current_user_id)
    except Exception:
        # If there's an error setting the audit fields (e.g., columns don't exist yet),
        # just continue without setting them
        pass


def get_current_user_id_from_request(request: Request) -> Optional[int]:
    """
    Get the current user ID from the request state
    
    Args:
        request: The current request
        
    Returns:
        The user ID if available in request state, None otherwise
    """
    return getattr(request.state, 'current_user_id', None)


async def get_current_user_id(current_user = Depends(get_current_user)) -> Optional[int]:
    """
    Get the current user ID from the authenticated user
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The user ID if authenticated, None otherwise
    """
    if current_user:
        return current_user.user_id
    return None


def with_audit_fields(db_obj: Any, data: Dict, current_user_id: Optional[int] = None, is_new: bool = True) -> Any:
    """
    Update a database object with data and add audit fields
    
    Args:
        db_obj: The database object to update
        data: The data to update the object with
        current_user_id: The ID of the current user (if available)
        is_new: Whether this is a new object (True) or an update (False)
        
    Returns:
        The updated database object
    """
    # Update object with provided data
    for key, value in data.items():
        setattr(db_obj, key, value)
    
    # Add audit fields
    add_audit_fields(db_obj, current_user_id, is_new)
    
    return db_obj