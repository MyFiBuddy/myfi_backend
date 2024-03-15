from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.portfolio_dao import PortfolioDAO
from myfi_backend.web.api.portfolio.schema import PortfolioDTO


async def get_portfolios(session: AsyncSession) -> List[PortfolioDTO]:
    """Retrieve portfolios for a specific user.

    :param session: Database session.
    :return: A list of PortfolioDTO objects for the user.
    """
    portfoliodao = PortfolioDAO(session)
    portfolios = await portfoliodao.get_all()

    def get_value_or_default(value: Any, default: Any) -> Any:
        return value if value is not None else default

    return [
        PortfolioDTO(
            portfolio_id=get_value_or_default(portfolio.id, 0),
            portfolio_name=get_value_or_default(portfolio.name, ""),
            portfolio_logo=get_value_or_default(portfolio.logo, ""),
            three_month_return=get_value_or_default(portfolio.three_month_return, 0),
            six_month_return=get_value_or_default(portfolio.six_month_return, 0),
            one_year_return=get_value_or_default(portfolio.one_year_return, 0),
            AssetDistribution={
                "equity_proportion": get_value_or_default(
                    portfolio.equity_proportion,
                    0,
                ),
                "debt_proportion": get_value_or_default(portfolio.debt_proportion, 0),
                "hybrid_proportion": get_value_or_default(
                    portfolio.hybrid_proportion,
                    0,
                ),
                "gold_proportion": get_value_or_default(portfolio.gold_proportion, 0),
                "index_fund_proportion": get_value_or_default(
                    portfolio.index_fund_proportion,
                    0,
                ),
                "other_proportion": get_value_or_default(portfolio.other_proportion, 0),
            },
        )
        for portfolio in portfolios
    ]
