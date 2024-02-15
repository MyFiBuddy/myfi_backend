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
