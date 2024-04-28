from typing import TYPE_CHECKING, List

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.amc_model import AMC
    from myfi_backend.db.models.portfolio_model import PortfolioMutualFund
    from myfi_backend.db.models.scheme_nav_model import SchemeNAV


class MutualFundScheme(BaseModel):
    """Model for Mutual Fund Schemes."""

    __tablename__ = "mutual_fund_schemes"

    name: Mapped[str] = mapped_column(
        String(length=200),
        unique=True,
        index=True,
        nullable=False,
    )
    # scheme_id: The ID of the Scheme.
    scheme_id = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )
    # amc_id: The ID of the AMC.
    amc_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("amcs.id"),
    )
    # scheme_plan: The plan of the scheme (e.g., direct, regular).
    scheme_plan: Mapped[str] = mapped_column(
        String(length=50),
        nullable=False,
    )
    # scheme_type: The type of the scheme (e.g., equity, debt, hybrid).
    scheme_type: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    # scheme_category: The category of the scheme (e.g., large cap, mid cap, small cap).
    scheme_category: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    # nav: The Net Asset Value of the scheme.
    nav: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # isin: The International Securities Identification Number of the scheme.
    isin: Mapped[str] = mapped_column(
        String(length=12),
        unique=True,
        nullable=False,
    )
    # cagr: The Compounded Annual Growth Rate of the scheme.
    cagr: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    # risk_level: The risk level of the scheme.
    risk_level: Mapped[str] = mapped_column(
        String(length=50),
        nullable=False,
    )
    # aum: The Assets Under Management of the scheme.
    aum: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # ter: The Total Expense Ratio of the scheme.
    ter: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # rating: The rating of the scheme.
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    # benchmark_index: The benchmark index of the scheme.
    benchmark_index: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    # min_investment_sip: The minimum investment for SIPs.
    min_investment_sip: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # min_investment_one_time: The minimum investment for one-time investments.
    min_investment_one_time: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # exit_load: The exit load of the scheme.
    exit_load: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    # fund_manager: The fund manager of the scheme.
    fund_manager: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    # return_since_inception: The return of the scheme since inception.
    return_since_inception: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # return_last_year: The return of the scheme over the last year.
    return_last_year: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # return_last3_years: The return of the scheme over the last 3 years.
    return_last3_years: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # return_last5_years: The return of the scheme over the last 5 years.
    return_last5_years: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    # standard_deviation: The standard deviation of the scheme.
    standard_deviation: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    # sharpe_ratio: The Sharpe ratio of the scheme.
    sharpe_ratio: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    # sortino_ratio: The Sortino ratio of the scheme.
    sortino_ratio: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    # alpha: The alpha of the scheme.
    alpha: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    # beta: The beta of the scheme.
    beta: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    # Relationship with AMC
    amc: Mapped["AMC"] = relationship(  # noqa: F821
        "AMC",
        back_populates="mutual_fund_schemes",
    )

    # Relationship with PortfolioMutualFund
    portfolios: Mapped[List["PortfolioMutualFund"]] = relationship(
        "PortfolioMutualFund",
        back_populates="mutualfundscheme",
    )

    # Relationship with SchemeNAV
    scheme_nav: Mapped[List["SchemeNAV"]] = relationship(
        "SchemeNAV",
        back_populates="mutualfundscheme",
    )
