from typing import List

from myfi_backend.web.api.scheme.schema import SchemeDTO


def get_schemes_from_db() -> List[SchemeDTO]:
    """
    Retrieve schemes from the database.

    :return: A list of schemes.
    """
    # Here you can handle the get_schemes_from_db data.
    # For example, you can save it to a database.
    # For now, let's just return it as is.
    return [
        SchemeDTO(
            scheme_id=1,
            scheme_name="Scheme 1",
            one_year_return=10.5,
            three_year_return=30.0,
            five_year_return=50.0,
        ),
        SchemeDTO(
            scheme_id=2,
            scheme_name="Scheme 2",
            one_year_return=15.0,
            three_year_return=35.0,
            five_year_return=55.0,
        ),
    ]
