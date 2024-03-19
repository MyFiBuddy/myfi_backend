from typing import Dict, List, Optional, cast
from uuid import UUID, uuid4

from myfi_backend.db.dao.scheme_nav_dao import SchemeNavDAO
from myfi_backend.web.api.scheme.schema import SchemeDTO, SchemeNavDTO


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
            scheme_id=uuid4(),
            scheme_name="Scheme 1",
            one_year_return=10.5,
            three_year_return=30.0,
            five_year_return=50.0,
        ),
        SchemeDTO(
            scheme_id=uuid4(),
            scheme_name="Scheme 2",
            one_year_return=15.0,
            three_year_return=35.0,
            five_year_return=55.0,
        ),
    ]


async def get_scheme_nav_from_db(
    schemenav_dao: SchemeNavDAO,
    scheme_id: UUID,
) -> Optional[SchemeNavDTO]:
    """
    Retrieve scheme NAV from the database.

    :param schemenav_dao: Database session.
    :param scheme_id: The ID of the scheme for which to retrieve the NAV.
    :return: The NAV of the scheme.
    """
    scheme_nav = await schemenav_dao.get_by_scheme_id(scheme_id)
    if scheme_nav and scheme_nav.nav_data is not None:
        nav_data = cast(Dict[str, float], scheme_nav.nav_data)
        return SchemeNavDTO(scheme_id=scheme_id, nav_data=nav_data)

    return None
