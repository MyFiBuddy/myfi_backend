import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.mutual_fund_scheme_dao import MutualFundSchemeDAO
from myfi_backend.db.models.amc_model import AMC
from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme


@pytest.mark.anyio
async def test_get_by_id_success(
    dbsession: AsyncSession,
    mutualfundscheme: MutualFundScheme,
) -> None:
    """Test getting a MutualFundScheme by id."""
    dao = MutualFundSchemeDAO(dbsession)
    result = await dao.get_by_id(uuid.UUID(str(mutualfundscheme.id)))
    assert result is not None


@pytest.mark.anyio
async def test_get_by_id_failure(dbsession: AsyncSession) -> None:
    """Test getting a MutualFundScheme by a non-existent id."""
    dao = MutualFundSchemeDAO(dbsession)
    result = await dao.get_by_id(
        uuid.UUID("00000000-0000-0000-0000-000000000000"),
    )  # non-existent id
    assert result is None


@pytest.mark.anyio
async def test_create_success(
    dbsession: AsyncSession,
    amc: AMC,
) -> None:
    """Test creating a new MutualFundScheme."""
    dao = MutualFundSchemeDAO(dbsession)
    result = await dao.create(
        {
            "name": "Test Scheme",
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
    )
    assert result is not None
    result_by_id = await dao.get_by_id(uuid.UUID(str(result.id)))
    assert result_by_id is not None
    assert result_by_id.name == "Test Scheme"
    assert result_by_id.amc_id == amc.id


@pytest.mark.anyio
async def test_update_success(
    dbsession: AsyncSession,
    mutualfundscheme: MutualFundScheme,
) -> None:
    """Test updating a MutualFundScheme."""
    dao = MutualFundSchemeDAO(dbsession)
    mutualfundscheme.name = "Updated MutualFundScheme Name"
    await dao.update(mutualfundscheme)
    result = await dao.get_by_id(uuid.UUID(str(mutualfundscheme.id)))
    assert result is not None
    assert result.name == "Updated MutualFundScheme Name"


@pytest.mark.anyio
async def test_get_amc_for_scheme(
    dbsession: AsyncSession,
    mutualfundscheme: MutualFundScheme,
    amc: AMC,
) -> None:
    """Test getting the AMC for a MutualFundScheme."""
    dao = MutualFundSchemeDAO(dbsession)
    result = await dao.get_by_id(uuid.UUID(str(mutualfundscheme.id)))
    assert result is not None
    assert result.amc_id == amc.id
