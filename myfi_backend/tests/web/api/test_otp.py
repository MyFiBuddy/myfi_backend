import json
import uuid
from typing import Dict, Union
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool, Redis
from starlette import status

from myfi_backend.utils.redis import REDIS_HASH_NEW_USER, generate_redis_key
from myfi_backend.web.api.otp.schema import OtpDTO, OtpResponseDTO, UserDTO


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_data",
    [
        {"email": "john.doe@example.com", "mobile": None},
        {"email": None, "mobile": "1234567890"},
        # Add more UserDTO instances here as needed.
    ],
)
async def test_signup_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake_redis_pool: ConnectionPool,
    user_data: Dict[str, Union[str, None]],
) -> None:
    """
    Tests that echo route works.

    :param fastapi_app: current application.
    :param client: client for the app.
    :param fake_redis_pool: fake redis pool.
    :param user_data: user data.
    """
    url = fastapi_app.url_path_for("signup")
    response = await client.post(
        url,
        json=user_data,
    )
    response_ob = OtpResponseDTO.parse_obj(response.json())
    assert response.status_code == status.HTTP_200_OK
    async with Redis(connection_pool=fake_redis_pool) as redis:
        assert response_ob.user_id is not None
        assert response_ob.message == "SUCCESS."
        redis_key = generate_redis_key(str(response_ob.user_id), REDIS_HASH_NEW_USER)
        redis_value = await redis.get(str(redis_key))
        assert redis_value is not None
        otp_data = OtpDTO.parse_raw(redis_value.decode("utf-8"))
        assert otp_data.otp is not None
        assert otp_data.user.user_id == response_ob.user_id
        assert otp_data.user.email == user_data["email"]
        assert otp_data.user.mobile == user_data["mobile"]


@pytest.mark.anyio
async def test_signup_failure(
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake_redis_pool: ConnectionPool,
) -> None:
    """
    Tests that signup fails when both user email and mobile are empty.

    :param fastapi_app: current application fixture.
    :param client: client fixture.
    """
    user_data = {
        "email": None,
        "mobile": None,
    }
    url = fastapi_app.url_path_for("signup")
    response = await client.post(url, json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid request."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_data",
    [
        {
            "email": "john.doe@example.com",
        },
        {
            "mobile": "1234567890",
        },
    ],
)
@patch("myfi_backend.web.api.otp.views.generate_otp")
async def test_verify_success(
    mock_generate_otp: MagicMock,
    fastapi_app: FastAPI,
    client: AsyncClient,
    user_data: Dict[str, Union[str, None]],
    fake_redis_pool: ConnectionPool,
) -> None:
    """
    Test case to verify the valid OTP with an email.

    :param fastapi_app: current application.
    :param client: client for the app.
    :param fake_redis_pool: fake redis pool.
    :param user_data: user data.
    """
    mock_generate_otp.return_value = "123456"
    signup_url = fastapi_app.url_path_for("signup")
    response = await client.post(
        signup_url,
        json=user_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_id"] is not None
    assert response.json()["message"] == "SUCCESS."

    user_id = response.json()["user_id"]

    user = UserDTO.parse_obj(user_data)
    user.user_id = user_id
    otp_data = OtpDTO(user=user, otp="123456")
    verify_url = fastapi_app.url_path_for("verify")
    response = await client.post(
        verify_url,
        json=otp_data.dict(),
    )

    assert response.status_code == status.HTTP_200_OK
    response_ob = OtpResponseDTO.parse_obj(response.json())
    assert response_ob.message == "SUCCESS."


@pytest.mark.anyio
async def test_verify_failure(
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake_redis_pool: ConnectionPool,
) -> None:
    """
    Test case to verify the resonse for bad request.

    :param fastapi_app: current application.
    :param client: client for the app.
    :param fake_redis_pool: fake redis pool.
    """
    # Mock otp_dict
    user_dto = UserDTO(
        email="john.doe@example.com",
        mobile="1234567890",
        user_id=uuid.uuid4(),
    )
    otp_data = OtpDTO(user=user_dto, otp="456789")
    verify_url = fastapi_app.url_path_for("verify")
    response = await client.post(
        verify_url,
        json=json.loads(
            otp_data.json(),
        ),  # need to convert to dict as uuid is not serializable
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found."
