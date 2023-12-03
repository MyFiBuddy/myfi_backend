from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from redis.asyncio import ConnectionPool

from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.utils.redis import REDIS_DUMMY_HASH, get_from_redis, set_to_redis
from myfi_backend.web.api.redis.schema import RedisValueDTO

router = APIRouter()


@router.get("/", response_model=RedisValueDTO)
async def get_redis_value(
    key: str,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> RedisValueDTO:
    """
    Get value from redis.

    :param key: redis key, to get data from.
    :param redis_pool: redis connection pool.
    :returns: information from redis.
    :raises HTTPException: If redis key is not found.
    """
    if key is None:
        return RedisValueDTO(
            key=key,
            value=None,
        )
    redis_value = await get_from_redis(redis_pool, key, REDIS_DUMMY_HASH)
    if redis_value is None:
        raise HTTPException(status_code=404, detail="Key not found.")
    return RedisValueDTO(
        key=key,
        value=redis_value,
    )


@router.put("/")
async def set_redis_value(
    redis_value: RedisValueDTO,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> None:
    """
    Set value in redis.

    :param redis_value: new value data.
    :param redis_pool: redis connection pool.
    :raises HTTPException: If redis value or key is None.
    """
    if not redis_value.key or not redis_value.value:
        raise HTTPException(status_code=400, detail="Key or value cannot be None.")
    await set_to_redis(
        redis_pool=redis_pool,
        key=redis_value.key,
        value=redis_value.value,
        hash_key=REDIS_DUMMY_HASH,
    )
