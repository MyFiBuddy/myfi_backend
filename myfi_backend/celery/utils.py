# flake8: noqa
import csv
import math
import os
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


async def parse_and_save_scheme_nav_data(
    data: Dict[str, Any],
    dbsession: AsyncSession,
) -> None:
    """
    Parse Scheme Nav data and save it to the database.

    :param data: The data to parse and save. This should be a dictionary.
    :param dbsession: The database session to use.
    """
    # Create a new session

    async with dbsession.begin():
        # Create a DAO object using the session
        scheme_nav_dao = SchemeNavDAO(dbsession)
        scheme_nav_data = {}
        for item in data:
            scheme = await MutualFundSchemeDAO(dbsession).get_by_code(
                data[item]["scheme_id"],
            )
            if scheme is None:
                continue
            else:
                scheme_nav_data = {
                    "scheme_id": scheme.id,
                    "nav_data": {data[item]["nav_date"]: data[item]["nav_value"]},
                }
            # Save the Scheme Nav data to the database
            await scheme_nav_dao.upsert(scheme_nav_data)


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

    Amc_Map = {
        "Baroda BNP": "771c0d62-b766-4497-a6f2-81d0ecddcf6b",
        "Aditya Birla Sun Life AMC Limited": "6ebc4add-fb55-423e-b870-d61a58618f69",
        # "Baroda Asset Management India Limited" :"0405312b-9fc8-44c5-9a81-6ede4b4cc5aa",
        "Canara": "5e0986ef-ccb0-4081-bfc8-7db9187ab620",
        "L&T": "fb23d5ca-bc37-4ec3-9872-42be44698bfb",
        "DSP": "c3eef640-3b63-4d52-80d7-083a219f4c03",
        "Quant ": "b6d2dd7c-7984-4e2b-ada1-2e41f31740a6",  # quant and quantum can conflict so had to add space.
        "Franklin": "671bc9c4-f4ff-4c72-a747-97c40a82c9f9",
        "HDFC": "7e396219-bdfe-424c-a828-95506e52ca8e",
        "HSBC": "a2380a64-8edb-4474-b7e4-ee931b5619d8",
        "ICICI": "bef2e060-057b-442b-a66c-6f8074fcc134",
        "JM": "1f6ef59b-85b3-4dad-a809-df3ea09d3580",
        "Kotak": "032a02b8-22cc-4e42-9060-841ee7ba47a2",
        "LIC": "dc525787-d9d6-49fd-bfec-bc69818d5c27",
        "Invesco": "d0fe114d-e41e-4c22-b192-ce7265784f95",
        "Quantum": "a856efc8-8d5c-448f-ae3b-138bfe078461",
        "Nippon": "9bdd759d-bbe5-4563-8f7a-4d81cf26ffcd",
        "SBI": "c6866fa0-88f7-4bcf-89e9-6f59a4474171",
        "IDFC": "e5c81c6a-d14c-4e67-8d5e-d0891a9cc24e",
        "Sundaram": "6e2edbb5-c4b3-43df-9f92-1e059ecf28bb",
        "Tata": "5a7281e7-bc39-4d5a-8e74-cc91be4b6cff",
        "Taurus": "c8e7cf4f-4f31-401e-8682-ada2ef60055b",
        "UTI": "227c9e4a-96d2-48f5-8427-7616c1b0d497",
        "Mirae": "9f6aa041-fb81-437c-a043-4e3108ea3f0c",
        "Bank of India": "1c5d873c-4a45-4e22-b728-f97b896f7b70",
        "Edelweiss": "51ef9f92-512f-45b4-a2bc-2086c11ff219",
        "Axis": "be4704a6-19b1-42c3-bc0e-7e1e36f2db30",
        "Navi": "c579faf7-645e-4e34-8aa3-4ea84303172d",
        "Motilal": "ddc9e98a-0766-448b-a8cf-9ef787ed237b",
        "IDBI": "a294ba7b-4125-4ce7-b50c-64562fe84429",
        "PGIM": "6bff126f-ca55-452f-bc16-9da67df63b7e",
        "Union": "75381d2b-06f9-4ac7-8b13-cb30e5ad5f1c",
        "IIFL": "602d731c-2a9f-458b-a621-759b51e1edd0",
        "Indiabulls": "73992762-df6d-4494-8c76-35d455de3f1c",
        "Parag": "2ba0a124-788b-4e2e-b318-ae7758d4f831",
        "IL&FS": "97a69b80-4270-4aa6-be4d-d19656c1ac6f",
        "Shriram": "858d902b-e5e5-4cd1-a0dd-25f42ecec749",
        "Mahindra": "97840f1d-d69e-4c50-b910-e3bb97c8db4b",
        "WhiteOak": "ba67dd81-767e-4246-8f0a-82d5a1e4c594",
        "ITI": "883d2af5-e991-4101-ac92-22fcec6447e3",
        "Trust": "fbafa554-f850-419c-bd83-3c372e839f15",
        "NJ": "61d44a7c-dc05-4881-8e73-18eed0a6934b",
        "Samco": "935a4760-e0e0-48f0-a50e-da46dda816d1",
    }
    input_path = os.path.join(
        os.getcwd(),
        "myfi_backend/scripts/scheme_data_22-May-2024_modified.csv",
    )
    output_path = os.path.join(
        os.getcwd(),
        "myfi_backend/celery/scheme_data_22-May-2024_final.csv",
    )
    with open(input_path, "r") as input_file:
        csvreader = csv.reader(input_file)
        with open(output_path, "w", newline="") as output_file:
            csvwriter = csv.writer(output_file)
            for row in csvreader:
                scheme_name = row[0]
                size = len(row)
                for key, value in Amc_Map.items():
                    key_len = len(key)
                    key = key.lower()
                    trim_scheme = scheme_name[:key_len]
                    trim_scheme = trim_scheme.lower()
                    if key == trim_scheme:
                        row.append(value)
                        csvwriter.writerow(row)

    Final_map = {}
    with open(output_path, "r") as input_file:
        csvreader = csv.reader(input_file)
        for row in csvreader:
            size = len(row) - 1
            scheme_name = row[0]
            amfi_code = row[1]
            Final_map[amfi_code] = {
                "name": row[0],
                "amfi_scheme_code": row[1],
                "benchmark": row[4],
                "plan": row[5],
                "scheme_category": row[6],
                "risk": row[9],
                "aum": row[10],
                "amc_uuid": row[size],
            }

    async with dbsession.begin():
        # Create a DAO object using the session
        scheme_dao = MutualFundSchemeDAO(dbsession)
        isin_code = 10000
        ZERO_FLOAT = 0.0
        for items in Final_map:
            scheme_data = {
                "name": str(Final_map[items]["name"]),
                "scheme_id": int(Final_map[items]["amfi_scheme_code"]),
                "amc_id": Final_map[items]["amc_uuid"],
                "scheme_plan": Final_map[items]["plan"],
                "scheme_type": Final_map[items]["plan"],
                "scheme_category": Final_map[items]["scheme_category"],
                "nav": 1.0 * isin_code,
                "isin": str(isin_code),
                "cagr": 1.0 * isin_code,
                "risk_level": Final_map[items]["risk"],
                "aum": float(Final_map[items]["aum"])
                if Final_map[items]["aum"]
                else ZERO_FLOAT,
                "ter": float(1.0 * isin_code),
                "rating": 0,
                "benchmark_index": str(Final_map[items]["benchmark"]),
                "min_investment_sip": float(1.0 * isin_code),
                "min_investment_one_time": 0,
                "exit_load": str(1.0 * isin_code),
                "fund_manager": str("XYZ"),
                "return_since_inception": float(1.0 * isin_code),
                "return_last_year": float(1.0 * isin_code),
                # if data[items]["return_last_year"]
                # else ZERO_FLOAT,
                "return_last3_years": float(1.0 * isin_code),
                # if data[items]["return_last3_year"]
                # else ZERO_FLOAT,
                "return_last5_years": float(1.0 * isin_code),
                # if data[items]["return_last5_year"]
                # else ZERO_FLOAT,
                "standard_deviation": float(1.0 * isin_code),
                # if data[items]["standard_deviation"]
                # else ZERO_FLOAT,
                "sharpe_ratio": float(1.0 * isin_code),
                # if data[items]["sharpe_ratio"]
                # else ZERO_FLOAT,
                "sortino_ratio": float(1.0 * isin_code),
                # if data[items]["sortino_ratio"]
                # else ZERO_FLOAT,
                "alpha": float(1.0 * isin_code),
                # if data[items]["alpha"]
                # else ZERO_FLOAT,
                "beta": float(1.0 * isin_code),
                # if data[items]["beta"]
                # else ZERO_FLOAT,
            }
            # Save the AMC data to the database
            isin_code += 10
            await scheme_dao.upsert(scheme_data)  # type: ignore


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
            "scheme_id": 11111,
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
            "scheme_id": 22222,
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
            "scheme_id": 33333,
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
            "scheme_id": 44444,
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
