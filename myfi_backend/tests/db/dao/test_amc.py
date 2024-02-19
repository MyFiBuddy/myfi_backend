import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from myfi_backend.db.dao.amc_dao import AmcDAO
from myfi_backend.db.dao.mutual_fund_scheme_dao import MutualFundSchemeDAO
from myfi_backend.db.models.amc_model import AMC


@pytest.mark.anyio
async def test_create_amc(dbsession: AsyncSession) -> None:
    """Test creating a AMC."""
    dao = AmcDAO(dbsession)
    amc = await dao.create(
        {
            "name": "New AMC",
            "code": "NEWAMC",
            "address": "New AMC Address",
            "email": "newamc@email.com",
            "phone": "1234567890",
            "website": "https://newamc.com",
            "fund_name": "New AMC Fund",
        },
    )
    await dbsession.commit()
    assert amc.id is not None


@pytest.mark.anyio
async def test_create_amc_without_name(dbsession: AsyncSession) -> None:
    """Test that AMC cannot be created without a name."""
    dao = AmcDAO(dbsession)

    with pytest.raises(IntegrityError):
        await dao.create({})
        await dbsession.commit()


@pytest.mark.anyio
async def test_create_amc_with_duplicate_name(dbsession: AsyncSession) -> None:
    """Test creating multiple AMC with same name."""
    amc_dao = AmcDAO(dbsession)
    await amc_dao.create(
        {
            "name": "Test AMC",
            "code": "NEWAMC",
            "address": "New AMC Address",
            "email": "newamc@email.com",
            "phone": "1234567890",
            "website": "https://newamc.com",
            "fund_name": "New AMC Fund",
        },
    )
    with pytest.raises(IntegrityError):
        await amc_dao.create(
            {
                "name": "Test AMC",
                "code": "NEWAMC",
                "address": "New AMC Address",
                "email": "newamc@email.com",
                "phone": "1234567890",
                "website": "https://newamc.com",
                "fund_name": "New AMC Fund",
            },
        )


@pytest.mark.anyio
async def test_upsert(dbsession: AsyncSession) -> None:
    """Test AMC upsert."""
    # Mock amc data
    amc_data = {
        "name": "Test AMC",
        "code": "123",
        "address": "Address 1 Address 2 Address 3",
        "email": "test@example.com",
        "phone": "1234567890",
        "website": "www.example.com",
        "fund_name": "Test Fund",
    }

    # Create a DAO object using the session
    amc_dao = AmcDAO(dbsession)

    # Call upsert function
    await amc_dao.upsert(amc_data)

    amc_data_updated = {
        "name": "Test AMC",
        "code": "123",
        "address": "Address 1 Address 2 Address 3",
        "email": "test_updated@example.com",  # Updated email
        "phone": "1234567890",
        "website": "www.example.com",
        "fund_name": "Test Fund",
    }

    # Call upsert function again
    await amc_dao.upsert(amc_data_updated)

    # Query the database for the inserted AMC data
    stmt = select(AMC).where(AMC.code == amc_data["code"])
    result = await dbsession.execute(stmt)
    db_amc = result.scalars().first()

    # Assert that the AMC data was inserted correctly
    assert db_amc is not None
    assert db_amc.name == amc_data["name"]
    assert db_amc.code == amc_data["code"]
    assert db_amc.address == amc_data["address"]
    assert db_amc.email == amc_data_updated["email"]  # check updated email
    assert db_amc.phone == amc_data["phone"]
    assert db_amc.website == amc_data["website"]
    assert db_amc.fund_name == amc_data["fund_name"]


@pytest.mark.anyio
async def test_amc_mutual_fund_schemes(dbsession: AsyncSession) -> None:
    """Test getting schemes for an amc."""
    amc_dao = AmcDAO(dbsession)
    amc = await amc_dao.create(
        {
            "name": "Test AMC",
            "code": "NEWAMC",
            "address": "New AMC Address",
            "email": "newamc@email.com",
            "phone": "1234567890",
            "website": "https://newamc.com",
            "fund_name": "New AMC Fund",
        },
    )

    scheme_dao = MutualFundSchemeDAO(dbsession)
    schemes = [
        await scheme_dao.create(
            {
                "name": "Test Scheme 1",
                "amc_id": uuid.UUID(str(amc.id)),
                "scheme_plan": "Test Plan",
                "scheme_type": "Test Type",
                "scheme_category": "Test Category",
                "nav": 10.0,
                "isin": "Test ISIN 1",
                "cagr": 5.0,
                "risk_level": "Test Risk Level",
                "aum": 1000000.0,
                "ter": 1.0,
                "rating": 5,
                "benchmark_index": "Test Benchmark Index",
                "min_investment_sip": 500.0,
                "min_investment_one_time": 5000.0,
                "exit_load": "Test Exit Load",
                "fund_manager": "Test Fund Manager",
                "return_since_inception": 10.0,
                "return_last_year": 5.0,
                "return_last3_years": 15.0,
                "return_last5_years": 25.0,
                "standard_deviation": 0.05,
                "sharpe_ratio": 1.0,
                "sortino_ratio": 1.0,
                "alpha": 0.1,
                "beta": 1.0,
            },
        ),
        await scheme_dao.create(
            {
                "name": "Test Scheme 2",
                "amc_id": uuid.UUID(str(amc.id)),
                "scheme_plan": "Test Plan",
                "scheme_type": "Test Type",
                "scheme_category": "Test Category",
                "nav": 10.0,
                "isin": "Test ISIN 2",
                "cagr": 5.0,
                "risk_level": "Test Risk Level",
                "aum": 1000000.0,
                "ter": 1.0,
                "rating": 5,
                "benchmark_index": "Test Benchmark Index",
                "min_investment_sip": 500.0,
                "min_investment_one_time": 5000.0,
                "exit_load": "Test Exit Load",
                "fund_manager": "Test Fund Manager",
                "return_since_inception": 10.0,
                "return_last_year": 5.0,
                "return_last3_years": 15.0,
                "return_last5_years": 25.0,
                "standard_deviation": 0.05,
                "sharpe_ratio": 1.0,
                "sortino_ratio": 1.0,
                "alpha": 0.1,
                "beta": 1.0,
            },
        ),
    ]
    await dbsession.commit()
    # Get the AMC
    result = await dbsession.execute(
        select(AMC)
        .where(AMC.id == amc.id)
        .options(
            selectinload(AMC.mutual_fund_schemes),
        ),
    )
    amc_from_db = result.scalars().first()
    assert amc_from_db is not None

    # Get the schemes of the AMC
    schemes_from_db = amc_from_db.mutual_fund_schemes
    assert schemes_from_db is not None
    assert len(schemes_from_db) == len(schemes)
    assert schemes_from_db[0].id == schemes[0].id
    assert schemes_from_db[0].name == "Test Scheme 1"
    assert schemes_from_db[0].amc_id == amc.id
    assert schemes_from_db[0].id == schemes[0].id
    assert schemes_from_db[1].name == "Test Scheme 2"
    assert schemes_from_db[1].amc_id == amc.id
    assert schemes_from_db[1].id == schemes[1].id
