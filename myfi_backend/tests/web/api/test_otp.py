import pytest
from fastapi import HTTPException

from myfi_backend.web.api.otp import views
from myfi_backend.web.api.otp.schema import (
    OtpDTO,
    SignupResponseDTO,
    UserDTO,
    VerifyResponseDTO,
)


@pytest.mark.anyio
async def test_signup_with_valid_user() -> None:
    """
    Test the signup function with a valid user.

    This test checks if the signup function returns the expected response when given a
    valid user. It also checks if the user's email or mobile number is added to the
    otp_dict.
    """
    user_data = {
        "email": "test@example.com",
        "mobile": "1234567890",
    }
    user = UserDTO.parse_obj(user_data)
    expected_response = SignupResponseDTO(message="OTP sent successfully.")

    response = await views.signup(user)

    assert response == expected_response
    assert user.email in views.otp_dict or user.mobile in views.otp_dict


@pytest.mark.anyio
async def test_signup_with_invalid_user() -> None:
    """
    Test the signup function with an invalid user.

    This test checks if the signup function raises an HTTPException when given an
    invalid user.
    """
    user_data = {
        "email": "",
        "mobile": "",
        "otp": 1234,
    }

    with pytest.raises(HTTPException):
        user = UserDTO.parse_obj(user_data)
        await views.signup(user)


@pytest.mark.anyio
async def test_verify_with_valid_email_otp() -> None:
    """
    Test case to verify the valid OTP with an email.

    It asserts that the response received is equal to the expected response.
    """
    # Mock otp_dict
    views.otp_dict = {"test@example.com": 1234, "1234567890": 1234}
    otp_data = {"email": "test@example.com", "otp": 1234}
    otp = OtpDTO.parse_obj(otp_data)
    expected_response = VerifyResponseDTO(message="OTP verified successfully.")

    response = await views.verify(otp)

    assert response == expected_response


@pytest.mark.anyio
async def test_verify_with_valid_mobile_otp() -> None:
    """
    Test case to verify the valid OTP with a mobile.

    It asserts that the response received is equal to the expected response.
    """
    # Mock otp_dict
    views.otp_dict = {"test@example.com": 1234, "1234567890": 1234}
    otp_data = {"mobile": "1234567890", "otp": 1234}
    otp = OtpDTO.parse_obj(otp_data)
    expected_response = VerifyResponseDTO(message="OTP verified successfully.")

    response = await views.verify(otp)

    assert response == expected_response


@pytest.mark.anyio
async def test_verify_with_invalid_email_otp() -> None:
    """
    Test case to verify the behavior of the 'verify' function.

    Test the expected behavour when an invalid email OTP is provided.

    Raises:
        HTTPException: If the OTP verification fails.
    """
    # Mock otp_dict
    views.otp_dict = {"test@example.com": 1234, "1234567890": 1234}
    otp_data = {"email": "test@example.com", "otp": 3455}

    with pytest.raises(HTTPException):
        otp = OtpDTO.parse_obj(otp_data)
        await views.verify(otp)


@pytest.mark.anyio
async def test_verify_with_invalid_mobile_otp() -> None:
    """Test case to verify the behavior of the 'verify' function.

    Test the expected behavour when an invalid mobile OTP is provided.

    Raises:
        HTTPException: If the OTP verification fails.
    """
    # Mock otp_dict
    views.otp_dict = {"test@example.com": 1234, "1234567890": 1234}
    otp_data = {"mobile": "1234567890", "otp": 3455}

    with pytest.raises(HTTPException):
        otp = OtpDTO.parse_obj(otp_data)
        await views.verify(otp)
