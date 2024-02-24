from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from myfi_backend.services.scheme.scheme_service import get_schemes_from_db

router = APIRouter()

from .schema import SchemeDTO

@router.get("/schemes/", response_model=List[SchemeDTO])
def get_schemes(user_id: UUID) -> List[SchemeDTO]:
    """
    Retrieve schemes based on user_id.
    """
    print("user_id", user_id)
    schemes = get_schemes_from_db(user_id)
    if schemes is None:
        raise HTTPException(status_code=404, detail="Schemes not found")
    return schemes