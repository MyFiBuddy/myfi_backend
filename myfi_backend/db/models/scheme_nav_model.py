from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme


class SchemeNAV(BaseModel):
    """Model for Scheme NAV data."""

    __tablename__ = "scheme_nav"

    # scheme_id: The ID of the Mutual Fund Scheme.
    scheme_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mutual_fund_schemes.id"),
        index=True,
        nullable=False,
    )
    # nav_data: The NAV data for the scheme.
    # format: {date: nav} e.g. {"2021-01-01": 100.0, "2021-01-02": 101.0}
    nav_data: Mapped[JSON] = mapped_column(JSON)

    # Establish a relationship with the MutualFundScheme model
    # Relationship with MutualFundScheme
    mutualfundscheme: Mapped["MutualFundScheme"] = relationship(
        "MutualFundScheme",
        back_populates="scheme_nav",
    )
