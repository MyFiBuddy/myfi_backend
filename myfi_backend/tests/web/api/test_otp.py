from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool, Redis
from starlette import status

from myfi_backend.utils.redis import REDIS_HASH_NEW_USER, generate_redis_key
from myfi_backend.web.api.otp.schema import (
    OtpDTO,
    OtpResponseDTO,
    PinDTO,
    SetPinResponseDTO,
    VerifyPinResponseDTO,
)
from myfi_backend.web.api.user.schema import UserDTO


@pytest.mark.anyio
@patch("myfi_backend.web.api.otp.views.generate_otp")
async def test_signup_success(
    mock_generate_otp: MagicMock,
    user_with_email: UserDTO,
    user_with_mobile: UserDTO,
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake_redis_pool: ConnectionPool,
) -> None:
    """
    Tests that echo route works.

    :param user_with_email: User data with email.
    :param user_with_mobile: User data with mobile.
    :param fastapi_app: current application.
    :param client: client for the app.
    :param fake_redis_pool: fake redis pool.
    """
    mock_generate_otp.return_value = "123456"
    url = fastapi_app.url_path_for("signup")
    for user in iter([user_with_email, user_with_mobile]):
        response = await client.post(
            url,
            json=user.dict(),
        )
        response_ob = OtpResponseDTO.parse_obj(response.json())
        assert response.status_code == status.HTTP_200_OK
        async with Redis(connection_pool=fake_redis_pool) as redis:
            assert response_ob.user_id is not None
            assert response_ob.is_existing_user is False
            assert response_ob.message == "SUCCESS."

            if user.email:
                redis_key = generate_redis_key(user.email, REDIS_HASH_NEW_USER)
            elif user.mobile:
                redis_key = generate_redis_key(user.mobile, REDIS_HASH_NEW_USER)
            redis_value = await redis.get(str(redis_key))

            assert redis_value is not None

            otp_data = OtpDTO.parse_raw(redis_value.decode("utf-8"))
            assert otp_data.user.user_id == response_ob.user_id

            if user.email:
                assert otp_data.email_otp == "123456"
                assert otp_data.mobile_otp is None
                assert otp_data.user.email == user.email
                assert otp_data.user.mobile is None
            elif user.mobile:
                assert otp_data.email_otp is None
                assert otp_data.mobile_otp == "123456"
                assert otp_data.user.mobile == user.mobile
                assert otp_data.user.email is None


@pytest.mark.anyio
@patch("myfi_backend.web.api.otp.views.generate_otp")
async def test_signup_existing_user(
    mock_generate_otp: MagicMock,
    user_with_email: UserDTO,
    user_with_mobile: UserDTO,
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """
    Test case to verify the signup process for an existing user.

    :param user_with_email: User data with email.
    :param user_with_mobile: User data with mobile.
    :param fastapi_app: current application.
    :param client: client for the app.
    """
    mock_generate_otp.return_value = "123456"
    user_ids = []

    # signup and verify new users
    for user_data in iter([user_with_email, user_with_mobile]):
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

        verify_url = fastapi_app.url_path_for("verify_otp")
        user_data.user_id = response.json()["user_id"]
        if user_data.email:
            otp_data = OtpDTO(user=user_data, email_otp="123456")
        elif user_data.mobile:
            otp_data = OtpDTO(user=user_data, mobile_otp="123456")
        response = await client.post(
            verify_url,
            json=otp_data.dict(),
        )
        assert response.status_code == status.HTTP_200_OK
        response_ob = OtpResponseDTO.parse_obj(response.json())
        assert response_ob.message == "SUCCESS."

    # signup existing users
    for user_data1 in iter([user_with_email, user_with_mobile]):
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
@patch("myfi_backend.web.api.otp.views.generate_otp")
async def test_verify_success(
    mock_generate_otp: MagicMock,
    user_with_email: UserDTO,
    user_with_mobile: UserDTO,
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake_redis_pool: ConnectionPool,
) -> None:
    """
    Test case to verify the valid OTP with an email.

    :param user_with_email: User data with email.
    :param user_with_mobile: User data with mobile.
    :param fastapi_app: current application.
    :param client: client for the app.
    :param fake_redis_pool: fake redis pool.
    """
    mock_generate_otp.return_value = "123456"
    signup_url = fastapi_app.url_path_for("signup")

    for user in iter([user_with_email, user_with_mobile]):
        response = await client.post(
            signup_url,
            json=user.dict(),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] is not None
        assert response.json()["message"] == "SUCCESS."

        user_id = response.json()["user_id"]

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
@patch("myfi_backend.web.api.otp.views.generate_otp")
async def test_verify_failure(
    mock_generate_otp: MagicMock,
    user_with_email: UserDTO,
    user_with_mobile: UserDTO,
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake_redis_pool: ConnectionPool,
) -> None:
    """
    Test case to verify the resonse for bad request.

    :mock_generate_otp: mock generate otp.
    :param user_with_email: User data with email.
    :param user_with_mobile: User data with mobile.
    :param fastapi_app: current application.
    :param client: client for the app.
    :param fake_redis_pool: fake redis pool.
    """
    mock_generate_otp.return_value = "123456"
    signup_url = fastapi_app.url_path_for("signup")

    for user in iter([user_with_email, user_with_mobile]):
        response = await client.post(
            signup_url,
            json=user.dict(),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] is not None
        assert response.json()["message"] == "SUCCESS."

        user_id = response.json()["user_id"]
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


@pytest.mark.anyio
@patch("myfi_backend.web.api.otp.views.generate_otp")
async def test_set_pin(
    mock_generate_otp: MagicMock,
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
    mock_generate_otp.return_value = "123456"
    user_ids = []

    # signup, verify, set and verify pin for new users
    for user_data in iter([user_with_email, user_with_mobile]):
        signup_url = fastapi_app.url_path_for("signup")
        response = await client.post(
            signup_url,
            json=user_data.dict(),
        )
        # signup
        assert response
        user_id = response.json()["user_id"]
        response_ob = OtpResponseDTO.parse_obj(response.json())
        assert response.status_code == status.HTTP_200_OK
        assert response_ob.user_id is not None
        assert response_ob.is_existing_user is False
        assert response_ob.message == "SUCCESS."
        user_ids.append(response_ob.user_id)

        # verify otp
        verify_url = fastapi_app.url_path_for("verify_otp")
        user_data.user_id = user_id
        assert user_data.user_id
        if user_data.email:
            otp_data = OtpDTO(user=user_data, email_otp="123456")
        elif user_data.mobile:
            otp_data = OtpDTO(user=user_data, mobile_otp="123456")
        response = await client.post(
            verify_url,
            json=otp_data.dict(),
        )
        assert response.status_code == status.HTTP_200_OK
        response_ob = OtpResponseDTO.parse_obj(response.json())
        assert response_ob.message == "SUCCESS."
        assert response_ob.user_id is not None

        # set pin
        set_pin_url = fastapi_app.url_path_for("set_pin")
        pin_data = PinDTO(user_id=user_id, pin="1234")
        response = await client.post(
            set_pin_url,
            json=pin_data.dict(),
        )
        assert response.status_code == status.HTTP_200_OK
        set_pin_response_ob = SetPinResponseDTO.parse_obj(response.json())
        assert set_pin_response_ob.message == "SUCCESS."

        # verify pin
        verify_pin_url = fastapi_app.url_path_for("verify_pin")
        pin_data = PinDTO(user_id=user_id, pin="1234")
        response = await client.post(
            verify_pin_url,
            json=pin_data.dict(),
        )
        assert response.status_code == status.HTTP_200_OK
        verify_pin_response_ob = VerifyPinResponseDTO.parse_obj(response.json())
        assert verify_pin_response_ob.message == "SUCCESS."
