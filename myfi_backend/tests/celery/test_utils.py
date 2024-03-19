from typing import Any, Callable, Coroutine, List
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.celery.utils import (
    insert_dummy_adviser,
    insert_dummy_amc,
    insert_dummy_organization,
    insert_dummy_portfolio,
    insert_dummy_portfolio_mutualfundscheme,
    insert_dummy_scheme_navs,
    insert_dummy_schemes,
    parse_and_save_amc_data,
)
from myfi_backend.db.models.adviser_model import Adviser
from myfi_backend.db.models.amc_model import AMC
from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme
from myfi_backend.db.models.organization_model import Organization
from myfi_backend.db.models.portfolio_model import Portfolio, PortfolioMutualFund
from myfi_backend.db.models.scheme_nav_model import SchemeNAV


@pytest.mark.anyio
async def test_parse_and_save_amc_data(dbsession: AsyncSession) -> None:
    """Test parsing and saving AMC data."""
    # Mock data
    data = {
        "Table": [
            {
                "amc": "Test AMC",
                "amc_code": "123",
                "add1": "Address 1",
                "add2": "Address 2",
                "add3": "Address 3",
                "email": "test@example.com",
                "phone": "1234567890",
                "webiste": "www.example.com",
                "fund": "Test Fund",
            },
        ],
    }

    # Call the function
    await parse_and_save_amc_data(data, dbsession)
    await dbsession.commit()
    # Get the AMC
    result = await dbsession.execute(select(AMC).where(AMC.code == "123"))
    amc_from_db = result.scalars().first()

    # Assert that the AMC data was inserted correctly
    assert amc_from_db is not None
    assert amc_from_db.name == "Test AMC"
    assert amc_from_db.code == "123"
    assert amc_from_db.address == "Address 1 Address 2 Address 3"
    assert amc_from_db.email == "test@example.com"
    assert amc_from_db.phone == "1234567890"
    assert amc_from_db.website == "www.example.com"
    assert amc_from_db.fund_name == "Test Fund"


@pytest.mark.anyio
async def test_insert_dummy_amc(dbsession: AsyncSession) -> None:
    """Test inserting dummy AMC."""
    # Create an AsyncMock instance
    mock_get_by_code = AsyncMock(return_value=None)

    # Mock the function you want to replace
    with patch("myfi_backend.db.dao.amc_dao.AmcDAO.get_by_code", new=mock_get_by_code):
        # Call the function
        amc_instance = await insert_dummy_amc(dbsession)

        # Check that the result is as expected
        assert amc_instance is not None


@pytest.mark.anyio
async def test_insert_dummy_schemes(dbsession: AsyncSession, amc: AMC) -> None:
    """Test inserting dummy schemes."""
    schemes = await insert_dummy_schemes(dbsession, amc)
    for scheme in schemes:
        result = await dbsession.execute(
            select(MutualFundScheme).where(MutualFundScheme.id == scheme.id),
        )
        fetched_scheme = result.scalars().first()
        assert fetched_scheme is not None
        assert fetched_scheme.amc_id == amc.id


@pytest.mark.anyio
async def test_insert_dummy_scheme_navs(dbsession: AsyncSession, amc: AMC) -> None:
    """Test inserting dummy scheme NAVs."""
    schemes = await insert_dummy_schemes(dbsession, amc)
    scheme_navs = await insert_dummy_scheme_navs(dbsession, schemes)
    for scheme_nav in scheme_navs:
        result = await dbsession.execute(
            select(SchemeNAV).where(SchemeNAV.id == scheme_nav.id),
        )
        fetched_scheme_nav = result.scalars().first()
        assert fetched_scheme_nav is not None
        assert fetched_scheme_nav.nav_data is not None
        assert fetched_scheme_nav.scheme_id in {scheme.id for scheme in schemes}


@pytest.mark.anyio
async def test_insert_dummy_organization(dbsession: AsyncSession) -> None:
    """Test inserting dummy organization."""
    organization = await insert_dummy_organization(dbsession)
    result = await dbsession.execute(
        select(Organization).where(Organization.id == organization.id),
    )
    fetched_organization = result.scalars().first()
    assert fetched_organization is not None
    assert fetched_organization.name == "Dummy Organization"
    assert fetched_organization.description == "Dummy Description"


@pytest.mark.anyio
async def test_insert_dummy_adviser(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """Test inserting dummy adviser."""
    adviser = await insert_dummy_adviser(dbsession, organization)
    result = await dbsession.execute(select(Adviser).where(Adviser.id == adviser.id))
    fetched_adviser = result.scalars().first()
    assert fetched_adviser is not None
    assert fetched_adviser.name == "Dummy Adviser"
    assert fetched_adviser.external_id == "Dummy external id"
    assert fetched_adviser.organization_id == organization.id


@pytest.mark.anyio
async def test_insert_dummy_portfolio(
    dbsession: AsyncSession,
    adviser: Adviser,
) -> None:
    """Test inserting dummy portfolios."""
    portfolios = await insert_dummy_portfolio(dbsession, adviser)
    for portfolio in portfolios:
        result = await dbsession.execute(
            select(Portfolio).where(Portfolio.id == portfolio.id),
        )
        fetched_portfolio = result.scalars().first()
        assert fetched_portfolio is not None
        assert fetched_portfolio.adviser_id == adviser.id


@pytest.mark.anyio
async def test_insert_dummy_portfolio_mutualfundscheme(
    dbsession: AsyncSession,
    portfolio: Portfolio,
    mutualfundschemes_factory: Callable[
        [int],
        Coroutine[Any, Any, List[MutualFundScheme]],
    ],
) -> None:
    """Test inserting dummy portfolio mutual fund schemes."""
    # create a list of schemes and then add schemes to the portfolio
    scheme_list = await mutualfundschemes_factory(5)
    await insert_dummy_portfolio_mutualfundscheme(dbsession, portfolio, scheme_list)
    for scheme in scheme_list:
        result = await dbsession.execute(
            select(PortfolioMutualFund).where(
                PortfolioMutualFund.mutualfundscheme_id == scheme.id,
            ),
        )
        fetched_portfolio_mutualfundscheme = result.scalars().first()
        assert fetched_portfolio_mutualfundscheme is not None
        assert fetched_portfolio_mutualfundscheme.portfolio_id == portfolio.id
