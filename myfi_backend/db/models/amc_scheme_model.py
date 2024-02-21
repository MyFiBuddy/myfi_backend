from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme


class SCHEME(BaseModel):
    """Model for Asset Management Companies."""

    __tablename__ = "schemes"

    code: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    fund_name: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )
    website: Mapped[str] = mapped_column(
        String(length=200),
        nullable=False,
    )

    # Relationship with MutualFundScheme
    mutual_fund_schemes: Mapped[List["MutualFundScheme"]] = relationship(  # noqa: F821
        "MutualFundScheme",
        back_populates="scheme",
    )
