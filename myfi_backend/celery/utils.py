from typing import Any, Dict

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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
from myfi_backend.settings import settings

db_url = make_url(str(settings.db_url.with_path("/postgres")))
engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def parse_and_save_amc_data(data: Dict[str, Any]) -> None:
    """
    Parse AMC data and save it to the database.

    :param data: The data to parse and save. This should be a dictionary.
    """
    # Create a new session
    async with session_factory() as session:
        # Begin a new transaction
        async with session.begin():
            # Create a DAO object using the session
            amc_dao = AmcDAO(session)

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
