from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from redis.asyncio import ConnectionPool

from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.services.scheme.scheme_service import get_schemes_from_db
from myfi_backend.utils.redis import REDIS_HASH_USER, get_from_redis
from myfi_backend.web.api.scheme.schema import SchemeDTO

router = APIRouter()


@router.get("/schemes/", response_model=List[SchemeDTO])
async def get_schemes(
    user_id: UUID,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> List[SchemeDTO]:
    """
    Retrieve schemes based on user_id.

    :param user_id: The user for whom to retrieve the schemes
    :param redis_pool: Redis connection pool.
    :return: A list of schemes for the user.
    :raises HTTPException: If the user ID is not provided or schemes not found.
    """
    value = await get_from_redis(
        redis_pool=redis_pool,
        key=str(user_id),
        hash_key=REDIS_HASH_USER,
    )
    if value is None:
        raise HTTPException(status_code=400, detail="Invalid request.")
    schemes = get_schemes_from_db(user_id)
    if schemes is None:
        raise HTTPException(status_code=404, detail="Schemes not found")
    return schemes
