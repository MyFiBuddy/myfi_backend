from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from myfi_backend.services.investment.investment_service import get_investment_values
from myfi_backend.web.api.investment.schema import InvestmentValueDTO

router = APIRouter()


@router.get("/user_investment_value/", response_model=List[InvestmentValueDTO])
async def user_investment_value(user_id: UUID) -> List[InvestmentValueDTO]:
    """
    Retrieve the investment values for a given user.

    :param user_id: The user for whom to retrieve the investment values.
    :return: AA list of investment values for the user.
    :raises HTTPException: If the user ID is not provided.

    """
    # Here you can handle the user_investment_value data.
    # For example, you can save it to a database.
    # For now, let's just return it as is.
    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID is required")

    return get_investment_values(user_id)
