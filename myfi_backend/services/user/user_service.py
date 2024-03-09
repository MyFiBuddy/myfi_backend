from uuid import UUID

from myfi_backend.web.api.user.schema import UserDTO


def get_user_from_db(user_id: UUID) -> UserDTO:
    """
    Retrieve a user from the database.

    :param user_id: The user for whom to retrieve the user.
    :return: A user for the user_id.
    """
    # Here you can handle the get_user_from_db data.
    # For example, you can save it to a database.
    # For now, let's just return it as is.
    return UserDTO(
        user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        user_name="John Doe",
        user_picture_url="https://example.com/user_picture.jpg",
    )
