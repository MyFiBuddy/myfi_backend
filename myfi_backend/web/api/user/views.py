from typing import Dict
from fastapi import APIRouter, HTTPException
from uuid import UUID

from myfi_backend.services.user.user_service import get_user_from_db
from myfi_backend.web.api.otp.schema import UserDTO

router = APIRouter()

@router.get("/" , response_model=Dict[str, UserDTO])
async def get_user(user_id: UUID) -> Dict[str, UserDTO]:
    """
    Retrieve a user based on user_id.
    """
    user = get_user_from_db(user_id)  # replace with your actual function to get a user from your database
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}
