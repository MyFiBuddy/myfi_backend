import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool, Redis
from starlette import status

from myfi_backend.utils.redis import REDIS_DUMMY_HASH, generate_redis_key


@pytest.mark.anyio
async def test_setting_value_success(
    fastapi_app: FastAPI,
    fake_redis_pool: ConnectionPool,
    client: AsyncClient,
) -> None:
    """
    Tests that you can set value in redis.

    :param fastapi_app: current application fixture.
    :param fake_redis_pool: fake redis pool.
    :param client: client fixture.
    """
    url = fastapi_app.url_path_for("set_redis_value")

    test_key = uuid.uuid4().hex
    test_val = uuid.uuid4().hex
    response = await client.put(
        url,
        json={
            "key": test_key,
            "value": test_val,
        },
    )

    redis_key = generate_redis_key(str(test_key), REDIS_DUMMY_HASH)
    assert response.status_code == status.HTTP_200_OK
    async with Redis(connection_pool=fake_redis_pool) as redis:
        actual_value = await redis.get(redis_key)
    assert actual_value.decode() == test_val


@pytest.mark.anyio
async def test_setting_value_failure(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """
    Tests that setting a None key or value to Redis raises an error.

    :param fastapi_app: current application fixture.
    :param client: client fixture.
    """
    test_key = "test_key"
    test_value = None
    url = fastapi_app.url_path_for("set_redis_value")
    response = await client.put(url, json={"key": test_key, "value": test_value})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Key or value cannot be None."


@pytest.mark.anyio
async def test_getting_value_success(
    fastapi_app: FastAPI,
    fake_redis_pool: ConnectionPool,
    client: AsyncClient,
) -> None:
    """
    Tests that you can get value from redis by key.

    :param fastapi_app: current application fixture.
    :param fake_redis_pool: fake redis pool.
    :param client: client fixture.
    """
    test_key = uuid.uuid4().hex
    test_val = uuid.uuid4().hex
    redis_key = generate_redis_key(str(test_key), REDIS_DUMMY_HASH)
    async with Redis(connection_pool=fake_redis_pool) as redis:
        await redis.set(redis_key, test_val)
    url = fastapi_app.url_path_for("get_redis_value")
    response = await client.get(url, params={"key": test_key})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["key"] == test_key
    assert response.json()["value"] == test_val


@pytest.mark.anyio
async def test_getting_value_failure(
    fastapi_app: FastAPI,
    fake_redis_pool: ConnectionPool,
    client: AsyncClient,
) -> None:
    """
    Tests that getting a non-existent key from Redis returns None.

    :param fastapi_app: current application fixture.
    :param fake_redis_pool: fake redis pool.
    :param client: client fixture.
    """
    test_key = uuid.uuid4().hex  # This key does not exist in Redis.
    url = fastapi_app.url_path_for("get_redis_value")
    response = await client.get(url, params={"key": test_key})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Key not found."
