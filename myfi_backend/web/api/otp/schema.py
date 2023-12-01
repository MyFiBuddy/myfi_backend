import uuid
from typing import Optional

from pydantic import BaseModel


class UserDTO(BaseModel):
    """Represents a user in the system.

    Attributes:
        email (Optional[str]): The user's email address.
        mobile (Optional[str]): The user's mobile phone number.
    """

    email: Optional[str] = None
    mobile: Optional[str] = None
    user_id: Optional[uuid.UUID] = None


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
    retry_count: Optional[int] = 0


class OtpResponseDTO(BaseModel):
    """
    Represents the response returned by the OTP verification API endpoint.

    Attributes:
        message: A message indicating the result of the verification process.
        user_id: The user ID of the user who was verified.
    """

    user_id: uuid.UUID
    message: str
