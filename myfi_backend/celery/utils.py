from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.amc_dao import AmcDAO
from myfi_backend.db.models.adviser_model import Adviser  # noqa: F401
from myfi_backend.db.models.amc_model import AMC  # noqa: F401
from myfi_backend.db.models.distributor_model import Distributor  # noqa: F401
from myfi_backend.db.models.employee_model import Employee  # noqa: F401
from myfi_backend.db.models.mutual_fund_scheme_model import (  # noqa: F401
    MutualFundScheme,
)
from myfi_backend.db.models.organization_model import Organization  # noqa: F401
from myfi_backend.db.models.portfolio_model import PortfolioMutualFund  # noqa: F401


async def parse_and_save_amc_data(
    data: Dict[str, Any],
    dbsession: AsyncSession,
) -> None:
    """
    Parse AMC data and save it to the database.

    :param data: The data to parse and save. This should be a dictionary.
    :param dbsession: The database session to use.
    """
    # Create a new session

    async with dbsession.begin():
        # Create a DAO object using the session
        amc_dao = AmcDAO(dbsession)

        for item in data["Table"]:
            # Create a dictionary containing the AMC data
            amc_data = {
                "name": item["amc"],
                "code": item["amc_code"],
                "address": f"{item['add1']} {item['add2']} {item['add3']}",
                "email": item["email"],
                "phone": item["phone"],
                "website": item["webiste"],
                "fund_name": item["fund"],
            }
            # Save the AMC data to the database
            await amc_dao.upsert(amc_data)
