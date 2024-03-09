from typing import Dict

from pydantic import BaseModel


class PortfolioDTO(BaseModel):
    """DTO for portfolios."""

    portfolio_id: int
    portfolio_name: str
    portfolio_logo: str
    three_month_return: float
    six_month_return: float
    one_year_return: float
    AssetDistribution: Dict[str, int]
