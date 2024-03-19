# flake8: noqa
import random
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.adviser_dao import AdviserDAO
from myfi_backend.db.dao.amc_dao import AmcDAO
from myfi_backend.db.dao.mutual_fund_scheme_dao import MutualFundSchemeDAO
from myfi_backend.db.dao.organization_dao import OrganizationDAO
from myfi_backend.db.dao.portfolio_dao import PortfolioDAO, PortfolioMutualFundDAO
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


async def parse_and_save_scheme_data(
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
        scheme_dao = MutualFundSchemeDAO(dbsession)
        isin_code = 0
        ZERO_FLOAT = 0.0
        for items in data:

            amc = await AmcDAO(dbsession).get_by_code(data[items]["amc_code"])
            if amc is None:
                continue
            else:
                scheme_data = {
                    "name": data[items]["name"],
                    "amc_id": amc.id,
                    "scheme_plan": data[items]["scheme_plan"],
                    "scheme_type": data[items]["scheme_type"],
                    "scheme_category": data[items]["scheme_category"],
                    "nav": float(data[items]["nav"])
                    if data[items]["nav"]
                    else ZERO_FLOAT,
                    "isin": str(isin_code),
                    "cagr": float(data[items]["cagr"])
                    if data[items]["cagr"]
                    else ZERO_FLOAT,
                    "risk_level": data[items]["risk_level"],
                    "aum": float(data[items]["aum"])
                    if data[items]["aum"]
                    else ZERO_FLOAT,
                    "ter": float(data[items]["ter"])
                    if data[items]["ter"]
                    else ZERO_FLOAT,
                    "rating": 0,
                    "benchmark_index": "A",
                    "min_investment_sip": float(data[items]["min_investment_sip"])
                    if data[items]["min_investment_sip"]
                    else ZERO_FLOAT,
                    "min_investment_one_time": 0,
                    "exit_load": data[items]["exit_load"],
                    "fund_manager": data[items]["fund_manager"],
                    "return_since_inception": float(
                        data[items]["return_since_inception"],
                    )
                    if data[items]["return_since_inception"]
                    else ZERO_FLOAT,
                    "return_last_year": float(data[items]["return_last_year"])
                    if data[items]["return_last_year"]
                    else ZERO_FLOAT,
                    "return_last3_years": float(data[items]["return_last3_year"])
                    if data[items]["return_last3_year"]
                    else ZERO_FLOAT,
                    "return_last5_years": float(data[items]["return_last5_year"])
                    if data[items]["return_last5_year"]
                    else ZERO_FLOAT,
                    "standard_deviation": float(data[items]["standard_deviation"])
                    if data[items]["standard_deviation"]
                    else ZERO_FLOAT,
                    "sharpe_ratio": float(data[items]["sharpe_ratio"])
                    if data[items]["sharpe_ratio"]
                    else ZERO_FLOAT,
                    "sortino_ratio": float(data[items]["sortino_ratio"])
                    if data[items]["sortino_ratio"]
                    else ZERO_FLOAT,
                    "alpha": float(data[items]["alpha"])
                    if data[items]["alpha"]
                    else ZERO_FLOAT,
                    "beta": float(data[items]["beta"])
                    if data[items]["beta"]
                    else ZERO_FLOAT,
                }
                # Save the AMC data to the database
                isin_code += 10
                await scheme_dao.upsert(scheme_data)


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
