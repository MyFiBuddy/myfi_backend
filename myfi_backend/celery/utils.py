import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.adviser_dao import AdviserDAO
from myfi_backend.db.dao.amc_dao import AmcDAO
from myfi_backend.db.dao.mutual_fund_scheme_dao import MutualFundSchemeDAO
from myfi_backend.db.dao.organization_dao import OrganizationDAO
from myfi_backend.db.dao.portfolio_dao import PortfolioDAO, PortfolioMutualFundDAO
from myfi_backend.db.dao.scheme_nav_dao import SchemeNavDAO
from myfi_backend.db.models.adviser_model import Adviser  # noqa: F401
from myfi_backend.db.models.amc_model import AMC  # noqa: F401
from myfi_backend.db.models.distributor_model import Distributor  # noqa: F401
from myfi_backend.db.models.employee_model import Employee  # noqa: F401
from myfi_backend.db.models.mutual_fund_scheme_model import (  # noqa: F401
    MutualFundScheme,
)
from myfi_backend.db.models.organization_model import Organization  # noqa: F401
from myfi_backend.db.models.portfolio_model import (  # noqa: F401
    Portfolio,
    PortfolioMutualFund,
)
from myfi_backend.db.models.scheme_nav_model import SchemeNAV  # noqa: F401


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


async def insert_dummy_data(  # noqa: WPS210
    dbsession: AsyncSession,
) -> None:
    """
    Insert dummy data into the database.

    :param dbsession: The database session to use.
    """
    amc = await insert_dummy_amc(dbsession)
    if amc:
        organization = await insert_dummy_organization(dbsession)
        scheme_list = await insert_dummy_schemes(dbsession, amc)
        await insert_dummy_scheme_navs(dbsession, scheme_list)
        adviser = await insert_dummy_adviser(dbsession, organization)
        portfolio_list = await insert_dummy_portfolio(dbsession, adviser)
        for portfolio in portfolio_list:
            await insert_dummy_portfolio_mutualfundscheme(
                dbsession,
                portfolio,
                scheme_list,
            )
    await dbsession.close()


async def insert_dummy_amc(
    dbsession: AsyncSession,
) -> Optional[AMC]:
    """
    Insert dummy data AMC into the database.

    :param dbsession: The database session to use.
    :return: The AMC model instance if inserted, else None.
    """
    amc_dao = AmcDAO(dbsession)
    if await amc_dao.get_by_code("12345"):
        return None
    amc = await amc_dao.create(
        {
            "name": "Dummy Fund",
            "code": "12345",
            "address": "Dummy 1 Address",
            "email": "dummy_email@email.com",
            "phone": "1234567890",
            "website": "https://dummy.com",
            "fund_name": "Dummy 1 Fund",
        },
    )
    await dbsession.commit()
    return amc


async def insert_dummy_schemes(
    dbsession: AsyncSession,
    amc: AMC,
) -> List[MutualFundScheme]:
    """
    Insert dummy mutual fund schemes into the database.

    :param dbsession: The database session to use.
    :param amc: The AMC model instance to associate the schemes with.
    :return: A list of MutualFundScheme model instances if inserted, else an empty list.
    """
    mutualfundscheme_dao = MutualFundSchemeDAO(dbsession)
    scheme_list: List[MutualFundScheme] = []
    schemes_data = [
        {
            "name": "Dummy Fund Healthcare Scheme",
            "amc_id": amc.id,
            "scheme_plan": "Dummy 1 Plan",
            "scheme_type": "Dummy 1 Type",
            "scheme_category": "Dummy 1 Category",
            "nav": 12.0,
            "isin": "Dummy1 ISIN",
            "cagr": 5.0,
            "risk_level": "Moderately High",
            "aum": 1000000.0,
            "ter": 1.0,
            "rating": 5,
            "benchmark_index": "Dummy 1 Benchmark Index",
            "min_investment_sip": 500.0,
            "min_investment_one_time": 5000.0,
            "exit_load": "Dummy 1 Exit Load",
            "fund_manager": "Dummy 1 Fund Manager",
            "return_since_inception": 80.0,
            "return_last_year": 5.0,
            "return_last3_years": 15.0,
            "return_last5_years": 25.0,
            "standard_deviation": 0.05,
            "sharpe_ratio": 1.0,
            "sortino_ratio": 1.0,
            "alpha": 0.1,
            "beta": 1.0,
        },
        {
            "name": "Dummy Fund Large Cap Scheme",
            "amc_id": amc.id,
            "scheme_plan": "Dummy 2 Plan",
            "scheme_type": "Dummy 2 Type",
            "scheme_category": "Dummy 2 Category",
            "nav": 15.5,
            "isin": "Dummy2 ISIN",
            "cagr": 5.0,
            "risk_level": "High",
            "aum": 1050000.0,
            "ter": 0.45,
            "rating": 4,
            "benchmark_index": "Dummy 2 Benchmark Index",
            "min_investment_sip": 100.0,
            "min_investment_one_time": 1000.0,
            "exit_load": "Dummy 2 Exit Load",
            "fund_manager": "Dummy 2 Fund Manager",
            "return_since_inception": 75.0,
            "return_last_year": 13.4,
            "return_last3_years": 42.5,
            "return_last5_years": 25.5,
            "standard_deviation": 0.5,
            "sharpe_ratio": 1.3,
            "sortino_ratio": 0.5,
            "alpha": 0.3,
            "beta": 0.7,
        },
        {
            "name": "Dummy Fund Mid Cap Scheme",
            "amc_id": amc.id,
            "scheme_plan": "Dummy 3 Plan",
            "scheme_type": "Dummy 3 Type",
            "scheme_category": "Dummy 3 Category",
            "nav": 25.3,
            "isin": "Dummy3 ISIN",
            "cagr": 5.0,
            "risk_level": "Very High",
            "aum": 2050500.0,
            "ter": 0.73,
            "rating": 3,
            "benchmark_index": "Dummy 3 Benchmark Index",
            "min_investment_sip": 100.0,
            "min_investment_one_time": 1000.0,
            "exit_load": "Dummy 3 Exit Load",
            "fund_manager": "Dummy 3 Fund Manager",
            "return_since_inception": 50.0,
            "return_last_year": 10.4,
            "return_last3_years": 42.5,
            "return_last5_years": 25.5,
            "standard_deviation": 0.5,
            "sharpe_ratio": 1.3,
            "sortino_ratio": 0.5,
            "alpha": 0.3,
            "beta": 0.7,
        },
        {
            "name": "Dummy Fund Bank Nifty Scheme",
            "amc_id": amc.id,
            "scheme_plan": "Dummy 4 Plan",
            "scheme_type": "Dummy 4 Type",
            "scheme_category": "Dummy 4 Category",
            "nav": 17.2,
            "isin": "Dummy4 ISIN",
            "cagr": 5.0,
            "risk_level": "Low",
            "aum": 3000800.0,
            "ter": 0.4,
            "rating": 4,
            "benchmark_index": "Dummy 4 Benchmark Index",
            "min_investment_sip": 100.0,
            "min_investment_one_time": 500.0,
            "exit_load": "Dummy 4 Exit Load",
            "fund_manager": "Dummy 4 Fund Manager",
            "return_since_inception": 120.0,
            "return_last_year": 10.8,
            "return_last3_years": 35.5,
            "return_last5_years": 52.8,
            "standard_deviation": 0.7,
            "sharpe_ratio": 0.3,
            "sortino_ratio": 0.5,
            "alpha": 0.8,
            "beta": 0.4,
        },
    ]

    for scheme_data in schemes_data:
        scheme = await mutualfundscheme_dao.create(scheme_data)
        scheme_list.append(scheme)
    await dbsession.commit()
    return scheme_list


async def insert_dummy_scheme_navs(
    dbsession: AsyncSession,
    schemes: List[MutualFundScheme],
) -> List[SchemeNAV]:
    """
    Insert dummy SchemeNAV entries into the database.

    :param dbsession: The database session to use.
    :param schemes: The MutualFundScheme model instances to associate the SchemeNAV
                    entries with.
    :return: A list of SchemeNAV model instances if inserted, else an empty list.
    """
    scheme_nav_dao = SchemeNavDAO(dbsession)
    scheme_nav_list: List[SchemeNAV] = []
    nav_data = {
        (datetime.now() - timedelta(days=index)).strftime("%Y-%m-%d"): 10.0
        + math.sin(index / 365.0) * 5
        for index in range(365 * 10)  # Generate data for the last 10 years
    }

    for scheme in schemes:
        scheme_nav = await scheme_nav_dao.create(
            {"scheme_id": scheme.id, "nav_data": nav_data},
        )
        scheme_nav_list.append(scheme_nav)
    await dbsession.commit()
    return scheme_nav_list


async def insert_dummy_organization(dbsession: AsyncSession) -> Organization:
    """
    Insert dummy organization into the database.

    :param dbsession: The database session to use.
    :return: Organization instance.
    """
    dao = OrganizationDAO(dbsession)
    organization = await dao.create(
        {
            "name": "Dummy Organization",
            "description": "Dummy Description",
        },
    )
    await dbsession.commit()
    return organization


async def insert_dummy_adviser(
    dbsession: AsyncSession,
    organization: Organization,
) -> Adviser:
    """
    Insert dummy adviser into the database.

    :param dbsession: The database session to use.
    :param organization: The organization to associate the adviser with.
    :return: Adviser instance.
    """
    dao = AdviserDAO(dbsession)
    adviser = await dao.create(
        {
            "name": "Dummy Adviser",
            "external_id": "Dummy external id",
            "organization_id": organization.id,
        },
    )
    await dbsession.commit()
    return adviser


async def insert_dummy_portfolio(
    dbsession: AsyncSession,
    adviser: Adviser,
) -> List[Portfolio]:
    """
    Insert dummy portfolios into the database.

    :param dbsession: The database session to use.
    :param adviser: The adviser to associate the portfolio with.
    :return: List of portfolio instances created.
    """
    portfolio_list: List[Portfolio] = []
    portfolio_dao = PortfolioDAO(dbsession)
    portfolio = await portfolio_dao.create(
        {
            "name": "Dummy Portfolio 1",
            "description": "This is a dummy portfolio 1",
            "risk_level": "Low",
            "equity_proportion": 20,
            "debt_proportion": 50,
            "hybrid_proportion": 10,
            "gold_proportion": 20,
            "adviser_id": adviser.id,  # Use the adviser fixture to get the adviser id
        },
    )
    portfolio_list.append(portfolio)
    portfolio = await portfolio_dao.create(
        {
            "name": "Dummy Portfolio 2",
            "description": "This is a dummy portfolio 2",
            "risk_level": "High",
            "equity_proportion": 50,
            "debt_proportion": 30,
            "hybrid_proportion": 10,
            "gold_proportion": 10,
            "adviser_id": adviser.id,  # Use the adviser fixture to get the adviser id
        },
    )
    portfolio_list.append(portfolio)
    await dbsession.commit()
    return portfolio_list


async def insert_dummy_portfolio_mutualfundscheme(  # noqa: WPS210
    dbsession: AsyncSession,
    portfolio: Portfolio,
    scheme_list: List[MutualFundScheme],
) -> None:
    """
    Insert schemes to dummy portfolio into the database.

    :param dbsession: The database session to use.
    :param portfolio: The portfolio to associate the schemes with.
    :param scheme_list: The list of schemes to associate with the portfolio.
    """
    portfolio_mutualfundscheme_dao = PortfolioMutualFundDAO(dbsession)
    # Create a list of random proportions for the schemes
    proportions = [random.random() for _ in range(len(scheme_list))]  # noqa: S311
    sum_proportions = sum(proportions)
    proportions = [
        round(100 * (proportion / sum_proportions)) for proportion in proportions
    ]
    # Adjust the last proportion so that the proportions add up to 100
    proportions[-1] = 100 - sum(proportions[:-1])
    for index, scheme in enumerate(scheme_list):
        proportion = proportions[index]
        await portfolio_mutualfundscheme_dao.create(
            {
                "portfolio_id": portfolio.id,
                "mutualfundscheme_id": scheme.id,
                "proportion": proportion,
            },
        )
    await dbsession.commit()
