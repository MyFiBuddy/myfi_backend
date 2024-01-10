from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme


class AMC(BaseModel):
    """Model for Asset Management Companies."""

    __tablename__ = "amcs"

    name: Mapped[str] = mapped_column(
        String(length=200),
        unique=True,
        index=True,
        nullable=False,
    )

    # Relationship with MutualFundScheme
    mutual_fund_schemes: Mapped[List["MutualFundScheme"]] = relationship(  # noqa: F821
        "MutualFundScheme",
        back_populates="amc",
    )
