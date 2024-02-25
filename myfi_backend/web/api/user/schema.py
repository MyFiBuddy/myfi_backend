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
    user_name: Optional[str] = None
    dob: Optional[str] = None
    user_picture_url: Optional[str] = None
