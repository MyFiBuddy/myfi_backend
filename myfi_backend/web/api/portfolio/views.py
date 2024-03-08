from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from redis.asyncio import ConnectionPool

from myfi_backend.services.portfolio.portfolio_service import get_portfolios
from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.utils.redis import REDIS_HASH_USER, get_from_redis
from myfi_backend.web.api.portfolio.schema import PortfolioDTO

router = APIRouter()


@router.get("/portfolios", response_model=List[PortfolioDTO])
async def get_portfolio(
    user_id: UUID,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> List[PortfolioDTO]:
    """
    Retrieve portfolios based on user_id.

    :param user_id: The user for whom to retrieve the portfolios
    :param redis_pool: Redis connection pool.
    :return: A list of portfolios for the user.
    :raises HTTPException: If the user ID is not provided or portfolios not found.
    """
    value = await get_from_redis(
        redis_pool=redis_pool,
        key=str(user_id),
        hash_key=REDIS_HASH_USER,
    )
    if value is None:
        raise HTTPException(status_code=400, detail="Invalid request.")
    portfolios = get_portfolios(user_id)
    if portfolios is None:
        raise HTTPException(status_code=404, detail="Portfolios not found")
    return portfolios
