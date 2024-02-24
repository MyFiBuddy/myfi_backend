import uuid
from myfi_backend.web.api.otp.schema import UserDTO
from uuid import UUID

def get_user_from_db(user_id: UUID) -> UserDTO:
    """
    Retrieve a user from the database.
    """
    # Here you can handle the get_user_from_db data.
    # For example, you can save it to a database.
    # For now, let's just return it as is.
    return UserDTO(
        email="johndoe@example.com",
        mobile="1234567890",
        user_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
        user_name="John Doe",
        dob="1990-01-01",
        user_picture_url="https://example.com/user_picture.jpg"
    )