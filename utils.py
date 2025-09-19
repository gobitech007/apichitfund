from typing import Optional
from fastapi import Depends, Request

from auth import get_current_user


async def get_current_user_id(request: Request, current_user = Depends(get_current_user)) -> Optional[int]:
    """
    Get the current user ID from either the authenticated user or the request state
    
    This function first tries to get the user ID from the authenticated user.
    If that fails, it falls back to the user ID stored in the request state by the middleware.
    
    Args:
        request: The current request
        current_user: The current authenticated user
        
    Returns:
        The user ID if available, None otherwise
    """
    try:
        # First try to get from authenticated user
        if current_user:
            return current_user.user_id
    except Exception:
        # If authentication fails, fall back to request state
        pass
    
    # Fall back to request state
    return getattr(request.state, 'current_user_id', None)

async def get_current_user_fullname(request: Request, current_user = Depends(get_current_user)) -> Optional[int]:
    """
    Get the current user ID from either the authenticated user or the request state
    
    This function first tries to get the user ID from the authenticated user.
    If that fails, it falls back to the user ID stored in the request state by the middleware.
    
    Args:
        request: The current request
        current_user: The current authenticated user
        
    Returns:
        The user ID if available, None otherwise
    """
    try:
        # First try to get from authenticated user
        if current_user:
            return current_user.fullname
    except Exception:
        # If authentication fails, fall back to request state
        pass
    
    # Fall back to request state
    return getattr(request.state, 'current_user_fullname', None)