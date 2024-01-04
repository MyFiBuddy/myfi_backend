from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from redis.asyncio import ConnectionPool

from myfi_backend.services.investment.investment_service import get_investment_values
from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.utils.redis import REDIS_HASH_USER, get_from_redis
from myfi_backend.web.api.investment.schema import InvestmentValueDTO

router = APIRouter()


@router.get("/user_investment_value/", response_model=List[InvestmentValueDTO])
async def user_investment_value(
    user_id: UUID,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> List[InvestmentValueDTO]:
    """
    Retrieve the investment values for a given user.

    :param user_id: The user for whom to retrieve the investment values.
    :param redis_pool: Redis connection pool.
    :return: A list of investment values for the user.
    :raises HTTPException: If the user ID is not provided.

    """
    # Here you can handle the user_investment_value data.
    # For example, you can save it to a database.
    # For now, let's just return it as is.
    value = await get_from_redis(
        redis_pool=redis_pool,
        key=str(user_id),
        hash_key=REDIS_HASH_USER,
    )
    if value is None:
        raise HTTPException(status_code=400, detail="Invalid request.")

    return get_investment_values(user_id)
