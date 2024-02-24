from typing import List
from uuid import UUID
from myfi_backend.web.api.scheme.schema import SchemeDTO

def get_schemes_from_db(user_id: UUID) -> List[SchemeDTO]:
    """
    Retrieve schemes from the database.
    """
    print("user_id", user_id)
    # Here you can handle the get_schemes_from_db data.
    # For example, you can save it to a database.
    # For now, let's just return it as is.
    return [
        SchemeDTO(scheme_id=1, scheme_name="Scheme 1", one_year_return=10.5, three_year_return=30.0, five_year_return=50.0),
        SchemeDTO(scheme_id=2, scheme_name="Scheme 2", one_year_return=15.0, three_year_return=35.0, five_year_return=55.0)
    ]