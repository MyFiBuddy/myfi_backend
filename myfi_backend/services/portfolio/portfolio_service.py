from typing import List
from uuid import UUID

from myfi_backend.web.api.portfolio.schema import PortfolioDTO


def get_portfolios(user_id: UUID) -> List[PortfolioDTO]:
    """Retrieve portfolios for a specific user.

    :param user_id: The user for whom to retrieve the user.
    :return: A list of PortfolioDTO objects for the user.
    """
    # function implementation
    return [
        PortfolioDTO(
            portfolio_id=1,
            portfolio_name="Portfolio 1",
            portfolio_logo="https://example.com/portfolio1.jpg",
            three_month_return=5.0,
            six_month_return=10.0,
            one_year_return=15.0,
            AssetDistribution={"Asset1": 50, "Asset2": 50},
        ),
        PortfolioDTO(
            portfolio_id=2,
            portfolio_name="Portfolio 2",
            portfolio_logo="https://example.com/portfolio2.jpg",
            three_month_return=6.0,
            six_month_return=12.0,
            one_year_return=18.0,
            AssetDistribution={"Asset1": 40, "Asset2": 60},
        ),
    ]
