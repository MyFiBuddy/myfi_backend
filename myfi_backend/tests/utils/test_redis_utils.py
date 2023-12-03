import pytest
from redis.asyncio import ConnectionPool

from myfi_backend.utils.redis import (
    REDIS_HASH_NEW_USER,
    delete_from_redis,
    generate_redis_key,
    get_from_redis,
    set_to_redis,
)


def test_generate_redis_key() -> None:
    """
    Test the generate_redis_key function.

    This test checks that the generate_redis_key function correctly concatenates
    the redis_hash_key and the key with a colon in between.
    """
    key = "test_key"
    redis_hash_key = "test_hash_key"
    expected_key = f"{redis_hash_key}:{key}"
    assert generate_redis_key(key, redis_hash_key) == expected_key


@pytest.mark.anyio
async def test_set_and_get_from_redis(fake_redis_pool: ConnectionPool) -> None:
    """
    Test the set_to_redis and get_from_redis function.

    This test checks that the set_to_redis function correctly sets a value in Redis
    given a key, value, and Redis connection pool.
    It also checks that the get_from_redis function correctly gets a value from Redis.
    """
    test_key = "test_key"
    test_value = "test_value"

    await set_to_redis(fake_redis_pool, test_key, test_value, REDIS_HASH_NEW_USER)
    value = await get_from_redis(fake_redis_pool, test_key, REDIS_HASH_NEW_USER)
    assert value == test_value


@pytest.mark.anyio
async def test_delete_from_redis(fake_redis_pool: ConnectionPool) -> None:
    """
    Test the delete_from_redis function.

    This test checks that the delete_from_redis function correctly deletes a value from
    Redis given a key and Redis connection pool.

    Parameters:
    - fake_redis_pool (ConnectionPool): The fake Redis connection pool.

    Returns:
    - None
    """
    test_key = "test_key"
    test_value = "test_value"

    await set_to_redis(fake_redis_pool, test_key, test_value, REDIS_HASH_NEW_USER)
    value = await get_from_redis(fake_redis_pool, test_key, REDIS_HASH_NEW_USER)
    assert value == test_value
    num_key_deleted = await delete_from_redis(
        fake_redis_pool,
        test_key,
        REDIS_HASH_NEW_USER,
    )
    assert num_key_deleted == 1
    value = await get_from_redis(fake_redis_pool, test_key, REDIS_HASH_NEW_USER)
    assert value is None
