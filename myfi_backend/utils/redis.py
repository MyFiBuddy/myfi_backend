from typing import Optional

from redis.asyncio import ConnectionPool, Redis

# redis hash for keys
REDIS_DUMMY_HASH = "DUMMY_HASH"
REDIS_HASH_USER = "REDIS_USER"
REDIS_HASH_SESSION = "REDIS_USER_SESSION"
REDIS_HASH_NEW_USER = "REDIS_NEW_USER"

# redis expiry time
REDIS_NEW_USER_EXPIRY_TIME = 180
REDIS_SESSION_EXPIRY_TIME = 3600 * 24 * 7


def generate_redis_key(key: str, redis_hash_key: str) -> str:
    """
    Generate a Redis key given a key string and a Redis hash key.

    :param key: The key string.
    :param redis_hash_key: The Redis hash key.

    :returns: The generated Redis key.
    """
    return f"{redis_hash_key}:{key}"


async def set_to_redis(
    redis_pool: ConnectionPool,
    key: str,
    value: str,
    hash_key: str,
    expire: Optional[int] = None,
) -> None:
    """
    Write a value to Redis.

    :param redis_pool: The Redis connection pool.
    :param key: The Redis key.
    :param value: The value to write to Redis.
    :param hash_key: The Redis hash key.
    :param expire: The number of seconds until the key expires. Set to -1 for no expiry.

    """
    redis_key = generate_redis_key(key, hash_key)
    async with Redis(connection_pool=redis_pool) as redis:
        await redis.set(name=redis_key, value=value, ex=expire)


async def get_from_redis(
    redis_pool: ConnectionPool,
    key: str,
    hash_key: str,
) -> Optional[str]:
    """
    Get a value from Redis.

    :param redis_pool: The Redis connection pool.
    :param key: The Redis key.
    :param hash_key: The Redis hash key.

    :returns: The value from Redis or None.
    """
    redis_key = generate_redis_key(key, hash_key)
    async with Redis(connection_pool=redis_pool) as redis:
        value = await redis.get(redis_key)
        return value.decode("utf-8") if value else None


async def delete_from_redis(
    redis_pool: ConnectionPool,
    key: str,
    hash_key: str,
) -> int:
    """
    Remove a key from Redis.

    :param redis_pool: The Redis connection pool.
    :param key: The Redis key.
    :param hash_key: The Redis hash key.

    :returns: The number of keys deleted.
    """
    redis_key = generate_redis_key(key, hash_key)
    async with Redis(connection_pool=redis_pool) as redis:
        return await redis.delete(redis_key)
