from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.adviser_model import Adviser
    from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme


class Portfolio(BaseModel):
    """
    Represents a portfolio in the database.

    Each portfolio consists of multiple mutual fund schemes.
    """

    __tablename__ = "portfolios"

    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=False)
    # adviser_id: The ID of the adviser the portfolio belongs to.
    adviser_id = mapped_column(UUID(as_uuid=True), ForeignKey("advisers.id"))
    # risk_level: The risk level of the portfolio.
    risk_level: Mapped[str] = mapped_column(String, nullable=False)
    # equity_proportion: The proportion of equity in the portfolio.
    equity_proportion: Mapped[int] = mapped_column(Integer, nullable=False)
    # debt_proportion: The proportion of debt in the portfolio.
    debt_proportion: Mapped[int] = mapped_column(Integer, nullable=False)
    # hybrid_proportion: The proportion of hybrid in the portfolio.
    hybrid_proportion: Mapped[int] = mapped_column(Integer, nullable=False)
    # gold_proportion: The proportion of gold in the portfolio.
    gold_proportion: Mapped[int] = mapped_column(Integer, default=0)
    # created_at: The timestamp when the portfolio was created.
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    # updated_at: The timestamp when the portfolio was last updated.
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationship to Adviser
    adviser: Mapped["Adviser"] = relationship(
        "Adviser",
        back_populates="portfolios",
    )

    # Relationship to PortfolioMutualFund
    mutual_fund_schemes: Mapped[List["PortfolioMutualFund"]] = relationship(
        "PortfolioMutualFund",
        back_populates="portfolio",
    )


class PortfolioMutualFund(BaseModel):
    """
    Represents a many-to-many relationship in the database.

    This model links a portfolio with its constituent mutual fund schemes.
    Each instance represents a specific mutual fund scheme and its proportion being
    part of a specific portfolio.
    """

    __tablename__ = "portfolio_mutualfundscheme"

    portfolio_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id"),
        primary_key=True,
    )
    mutualfundscheme_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mutual_fund_schemes.id"),
        primary_key=True,
    )
    proportion: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )  # Proportion as a percentage

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="mutual_fund_schemes",
    )
    mutualfundscheme: Mapped["MutualFundScheme"] = relationship(
        "MutualFundScheme",
        back_populates="portfolios",
    )
