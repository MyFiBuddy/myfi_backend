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
        assert response_ob.is_existing_user is False
        assert response_ob.message == "SUCCESS."

        if user_data["email"]:
            redis_key = generate_redis_key(user_data["email"], REDIS_HASH_NEW_USER)
        elif user_data["mobile"]:
            redis_key = generate_redis_key(user_data["mobile"], REDIS_HASH_NEW_USER)
        redis_value = await redis.get(str(redis_key))

        assert redis_value is not None

        otp_data = OtpDTO.parse_raw(redis_value.decode("utf-8"))
        assert otp_data.user.user_id == response_ob.user_id

        if user_data["email"]:
            assert otp_data.email_otp is not None
            assert otp_data.mobile_otp is None
            assert otp_data.user.email == user_data["email"]
            assert otp_data.user.mobile is None
        elif user_data["mobile"]:
            assert otp_data.email_otp is None
            assert otp_data.mobile_otp is not None
            assert otp_data.user.mobile == user_data["mobile"]
            assert otp_data.user.email is None


@pytest.mark.anyio
async def test_signup_existing_user(
    user_with_email: UserDTO,
    user_with_mobile: UserDTO,
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """
    Test case to verify the signup process for an existing user.

    param user_with_email: User data with email.
    param user_with_mobile: User data with mobile.
    param fastapi_app: current application.
    param client: client for the app.
    """
    user_ids = []
    user_data_list = [user_with_email, user_with_mobile]

    for user_data in user_data_list:
        signup_url = fastapi_app.url_path_for("signup")
        response = await client.post(
            signup_url,
            json=user_data.dict(),
        )
        assert response
        response_ob = OtpResponseDTO.parse_obj(response.json())
        assert response.status_code == status.HTTP_200_OK
        assert response_ob.user_id is not None
        assert response_ob.is_existing_user is False
        assert response_ob.message == "SUCCESS."
        user_ids.append(response_ob.user_id)

    user_data_list = [user_with_email, user_with_mobile]

    for user_data1 in user_data_list:
        signup_url = fastapi_app.url_path_for("signup")
        response = await client.post(
            signup_url,
            json=user_data1.dict(),
        )
        response_ob = OtpResponseDTO.parse_obj(response.json())
        assert response.status_code == status.HTTP_200_OK
        assert response_ob.user_id is not None
        assert response_ob.is_existing_user is True
        assert response_ob.message == "SUCCESS."
        assert response_ob.user_id in user_ids


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

    if user.email:
        otp_data = OtpDTO(user=user, email_otp="123456")
    elif user.mobile:
        otp_data = OtpDTO(user=user, mobile_otp="123456")

    verify_url = fastapi_app.url_path_for("verify_otp")
    response = await client.post(
        verify_url,
        json=otp_data.dict(),
    )

    assert response.status_code == status.HTTP_200_OK
    response_ob = OtpResponseDTO.parse_obj(response.json())
    assert response_ob.message == "SUCCESS."


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
async def test_verify_failure(
    mock_generate_otp: MagicMock,
    fastapi_app: FastAPI,
    client: AsyncClient,
    user_data: Dict[str, Union[str, None]],
    fake_redis_pool: ConnectionPool,
) -> None:
    """
    Test case to verify the resonse for bad request.

    :mock_generate_otp: mock generate otp.
    :param fastapi_app: current application.
    :param client: client for the app.
    :param user_data: user data.
    :param fake_redis_pool: fake redis pool.
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

    if user.email:
        otp_data = OtpDTO(user=user, email_otp="111111")
    elif user.mobile:
        otp_data = OtpDTO(user=user, mobile_otp="111111")

    verify_url = fastapi_app.url_path_for("verify_otp")
    response = await client.post(
        verify_url,
        json=otp_data.dict(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid request."
