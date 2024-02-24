import uuid
from typing import Optional, Union

from pydantic import BaseModel, validator

from myfi_backend.web.api.user.schema import UserDTO

class OtpDTO(BaseModel):
    """Represents a one-time password (OTP) used for authentication.

    Attributes:
        user: The user associated with the OTP.
        email_otp (int): The OTP value for email.
        mobile_otp (int): The OTP value for mobile.
        retry_count (int): The number of times the user has retried the OTP.
    """

    user: UserDTO
    email_otp: Optional[str] = None
    mobile_otp: Optional[str] = None
    pin: Optional[str] = None
    retry_count: Optional[int] = 0


class OtpResponseDTO(BaseModel):
    """
    Represents the response returned by the OTP verification API endpoint.

    Attributes:
        user_id: The user ID of the user who was verified.
        is_existing_user: A boolean indicating whether the user is an existing user.
        message: A message indicating the result of the verification process.
    """

    user_id: uuid.UUID
    is_existing_user: bool = False
    message: str


class PinDTO(BaseModel):
    """
    Represents the data required to set or verify a PIN.

    Attributes:
        user_id: The user ID of the user who is setting or verifying the PIN.
        pin: The PIN to be set or verified.
    """

    user_id: uuid.UUID
    pin: str

    @validator("user_id")
    def validate_uuids(cls, value: uuid.UUID) -> Union[str, uuid.UUID]:  # noqa: N805
        """
        Validate and convert UUIDs to strings.

        :param value: The UUID to validate and convert.

        :return: The UUID as a string if it's valid, or the original value if it's not.
        """
        if value:
            return str(value)
        return value


class SetPinResponseDTO(BaseModel):
    """
    Represents the response returned by the set_pin API endpoint.

    Attributes:
        user_id: The user ID of the user who set the PIN.
        message: A message indicating the result of the PIN setting process.
    """

    user_id: uuid.UUID
    message: str


class VerifyPinResponseDTO(BaseModel):
    """
    Represents the response returned by the verify_pin API endpoint.

    Attributes:
        user_id: The user ID of the user who verified the PIN.
        is_verified: A boolean indicating whether the PIN was verified successfully.
        message: A message indicating the result of the PIN verification process.
    """

    user_id: uuid.UUID
    is_verified: bool = False
    message: str
