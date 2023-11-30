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
        otp (int): The OTP value.
    """

    user: UserDTO
    otp: str
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
