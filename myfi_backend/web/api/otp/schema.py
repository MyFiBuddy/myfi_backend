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
        email (Optional[str]): The email address associated with the OTP.
        mobile (Optional[str]): The mobile number associated with the OTP.
        otp (int): The OTP value.
    """

    email: Optional[str] = None
    mobile: Optional[str] = None
    otp: int


class SignupResponseDTO(BaseModel):
    """
    Represents the response returned by the server after a user signs up.

    Attributes:
        message (str): A message indicating the result of the signup attempt.
    """

    message: str


class VerifyResponseDTO(BaseModel):
    """
    Represents the response returned by the OTP verification API endpoint.

    Attributes:
        message (str): A message indicating the result of the verification process.
    """

    message: str
