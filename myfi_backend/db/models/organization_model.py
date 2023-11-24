from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.adviser_model import Adviser
    from myfi_backend.db.models.distributer_model import Distributor
    from myfi_backend.db.models.employee_model import Employee


class Organization(BaseModel):
    """Model for organizations."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(length=200),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(length=200),
        nullable=True,
    )

    # Relationships with Distributor and Adviser
    distributors: Mapped[List["Distributor"]] = relationship(  # noqa: F821
        "Distributor",
        back_populates="organization",
    )
    advisers: Mapped[List["Adviser"]] = relationship(  # noqa: F821
        "Adviser",
        back_populates="organization",
    )
    employees: Mapped[List["Employee"]] = relationship(  # noqa: F821
        "Employee",
        back_populates="organization",
    )
