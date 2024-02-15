from typing import Any, Callable, Coroutine, List, Tuple

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.db.dao.portfolio_dao import PortfolioDAO, PortfolioMutualFundDAO
from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme
from myfi_backend.db.models.portfolio_model import Portfolio, PortfolioMutualFund


@pytest.mark.anyio
async def test_create_portfolio(dbsession: AsyncSession) -> None:
    """Test creating a Portfolio instance."""
    portfolio_dao = PortfolioDAO(dbsession)
    portfolio = await portfolio_dao.create(
        {
            "name": "Test Portfolio",
            "description": "This is a test portfolio",
            "risk_level": "Low",
            "equity_proportion": 40,
            "debt_proportion": 30,
            "hybrid_proportion": 20,
            "gold_proportion": 10,
        },
    )
    await dbsession.commit()

    assert portfolio.id is not None
    assert portfolio.name == "Test Portfolio"


@pytest.mark.anyio
async def test_get_portfolio(dbsession: AsyncSession, portfolio: Portfolio) -> None:
    """Test getting a Portfolio instance."""
    portfolio_dao = PortfolioDAO(dbsession)
    fetched_portfolio = await portfolio_dao.get_by_id(portfolio.id)

    assert fetched_portfolio is not None
    assert fetched_portfolio.id == portfolio.id
    assert fetched_portfolio.name == portfolio.name


@pytest.mark.anyio
async def test_update_portfolio(dbsession: AsyncSession, portfolio: Portfolio) -> None:
    """Test updating a Portfolio instance."""
    created_at = portfolio.created_at
    updated_at = portfolio.updated_at
    portfolio_dao = PortfolioDAO(dbsession)
    portfolio.name = "Updated Portfolio"
    await portfolio_dao.update(portfolio)

    fetched_portfolio = await portfolio_dao.get_by_id(portfolio.id)
    assert fetched_portfolio is not None

    assert fetched_portfolio.name == "Updated Portfolio"
    assert fetched_portfolio.created_at == created_at
    assert fetched_portfolio.updated_at > updated_at  # type: ignore


@pytest.mark.anyio
async def test_delete_portfolio(dbsession: AsyncSession, portfolio: Portfolio) -> None:
    """Test deleting a Portfolio instance."""
    portfolio_dao = PortfolioDAO(dbsession)
    await portfolio_dao.delete(portfolio.id)

    fetched_portfolio = await portfolio_dao.get_by_id(portfolio.id)
    assert fetched_portfolio is None


@pytest.mark.anyio
async def test_add_mutualfundscheme_to_portfolio(  # noqa: WPS234
    dbsession: AsyncSession,
    mutualfundschemes_with_proportions_factory: Callable[
        [int],
        Coroutine[Any, Any, List[Tuple[MutualFundScheme, int]]],
    ],
    portfolio: Portfolio,
) -> None:  # noqa: WPS234
    """Test adding a MutualFundScheme to a Portfolio."""
    # Create a new DAO instance
    portfolio_dao = PortfolioDAO(dbsession)
    portfolio_mutualfundscheme_dao = PortfolioMutualFundDAO(dbsession)
    # Create new PortfolioMutualFund instances for each MutualFundScheme
    mutualfundschemes_with_proportions = (
        await mutualfundschemes_with_proportions_factory(5)
    )
    for mutualfundscheme, proportion in mutualfundschemes_with_proportions:
        await portfolio_mutualfundscheme_dao.create(
            {
                "portfolio_id": portfolio.id,
                "mutualfundscheme_id": mutualfundscheme.id,
                "proportion": proportion,
            },
        )

    await dbsession.commit()

    # Now the portfolio should have the mutual fund schemes
    fetched_portfolio = await portfolio_dao.get_by_id(portfolio.id)
    assert fetched_portfolio is not None
    fetched_mutual_fund_schemes = fetched_portfolio.mutual_fund_schemes
    assert len(fetched_mutual_fund_schemes) == 5

    # Check that the mutual_fund_schemes in the fetched portfolio have the expected
    # mutualfundscheme_id and proportion
    for (
        mutualfundscheme_original,
        proportion_original,
    ) in mutualfundschemes_with_proportions:
        assert any(
            portfolio_mutualfundscheme.mutualfundscheme_id
            == mutualfundscheme_original.id
            and portfolio_mutualfundscheme.proportion == proportion_original
            for portfolio_mutualfundscheme in fetched_mutual_fund_schemes
        )


@pytest.mark.anyio
async def test_update_mutualfundschemes_in_portfolio(  # noqa: WPS234
    dbsession: AsyncSession,
    mutualfundschemes_with_proportions_factory: Callable[
        [int],
        Coroutine[Any, Any, List[Tuple[MutualFundScheme, int]]],
    ],
    portfolio: Portfolio,
) -> None:
    """Test updating MutualFundScheme of a Portfolio."""
    # Set up initial data
    portfolio_mutualfundscheme_dao = PortfolioMutualFundDAO(dbsession)
    mf_schemes_with_proportions = await mutualfundschemes_with_proportions_factory(5)

    mf_schemes_proportions_ids_original = [
        (mutualfundscheme.id, proportion)
        for mutualfundscheme, proportion in mf_schemes_with_proportions
    ]

    # Call the function
    await portfolio_mutualfundscheme_dao.update_schemes_in_portfolio(
        portfolio.id,
        mf_schemes_proportions_ids_original,
    )

    # Update the portfolio with new schemes and proportions
    mf_schemes_with_proportions_updated = (
        await mutualfundschemes_with_proportions_factory(5)
    )

    mf_schemes_proportions_ids_updated = [
        (mutualfundscheme.id, proportion)
        for mutualfundscheme, proportion in mf_schemes_with_proportions_updated
    ]

    await portfolio_mutualfundscheme_dao.update_schemes_in_portfolio(
        portfolio.id,
        mf_schemes_proportions_ids_updated,
    )

    # Check that the data was updated as expected
    result = await dbsession.execute(
        select(PortfolioMutualFund).where(
            PortfolioMutualFund.portfolio_id == portfolio.id,
        ),
    )
    updated_schemes = result.scalars().all()

    for scheme in updated_schemes:
        assert any(
            scheme.mutualfundscheme_id == mutualfundscheme.id
            and scheme.proportion == proportion
            for mutualfundscheme, proportion in mf_schemes_with_proportions_updated
        )


@pytest.mark.anyio
async def test_create_portfolio_mutual_fund(
    dbsession: AsyncSession,
    portfolio: Portfolio,
    mutualfundscheme: MutualFundScheme,
) -> None:
    """Test creating a PortfolioMutualFund."""
    # Create a new DAO instance
    portfolio_mutualfundscheme_dao = PortfolioMutualFundDAO(dbsession)
    # Create a new PortfolioMutualFund instance
    portfolio_mutualfundscheme = await portfolio_mutualfundscheme_dao.create(
        {
            "portfolio_id": portfolio.id,
            "mutualfundscheme_id": mutualfundscheme.id,
            "proportion": 50,
        },
    )
    await dbsession.commit()
    # Check that the PortfolioMutualFund was created correctly
    assert portfolio_mutualfundscheme.id is not None
    assert portfolio_mutualfundscheme.portfolio_id == portfolio.id
    assert portfolio_mutualfundscheme.mutualfundscheme_id == mutualfundscheme.id
    assert portfolio_mutualfundscheme.proportion == 50


@pytest.mark.anyio
async def test_get_portfolio_mutual_fund_by_id(
    dbsession: AsyncSession,
    portfolio_mutualfundscheme: PortfolioMutualFund,
) -> None:
    """Test getting a PortfolioMutualFund by its ID."""
    # Create a new DAO instance
    portfolio_mutualfundscheme_dao = PortfolioMutualFundDAO(dbsession)
    # Get the PortfolioMutualFund by its ID
    fetched_portfolio_mutualfundscheme = await portfolio_mutualfundscheme_dao.get_by_id(
        portfolio_mutualfundscheme.id,
    )
    # Check that the fetched PortfolioMutualFund is the same as the original one
    assert fetched_portfolio_mutualfundscheme == portfolio_mutualfundscheme
