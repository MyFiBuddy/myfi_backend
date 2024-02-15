from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.organization_model import Organization
    from myfi_backend.db.models.portfolio_model import Portfolio


class Adviser(BaseModel):
    """Model for advisers."""

    __tablename__ = "advisers"

    external_id: Mapped[str] = mapped_column(
        String(length=200),
        unique=True,
        index=True,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(length=200),
        unique=False,
        index=True,
        nullable=False,
    )
    organization_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
    )

    # Relationship with Organization
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        "Organization",
        back_populates="advisers",
    )

    # Relationship with Portfolio
    portfolios: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="adviser",
    )
