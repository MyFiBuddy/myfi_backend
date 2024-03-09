from typing import Dict
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from redis.asyncio import ConnectionPool

from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.services.user.user_service import get_user_from_db
from myfi_backend.utils.redis import REDIS_HASH_USER, get_from_redis
from myfi_backend.web.api.user.schema import UserDTO

router = APIRouter()


@router.get("/user", response_model=Dict[str, UserDTO])
async def get_user(
    user_id: UUID,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> Dict[str, UserDTO]:
    """
    Retrieve a user based on user_id.

    :param user_id: The user for whom to retrieve the user.
    :param redis_pool: Redis connection pool.
    :return: A user for the user_id.
    :raises HTTPException: If the user ID is not found or user details not found.
    """
    value = await get_from_redis(
        redis_pool=redis_pool,
        key=str(user_id),
        hash_key=REDIS_HASH_USER,
    )
    if value is None:
        raise HTTPException(status_code=400, detail="Oopsie! Unable to access that")
    user = get_user_from_db(
        user_id,
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Oops! Something went wrong")
    return {"user": user}
