from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from myfi_backend.db.models.base_model import BaseModel

if TYPE_CHECKING:
    from myfi_backend.db.models.organization_model import Organization


class Employee(BaseModel):
    """
    Model for employees.

    Attributes:
        id (int): The primary key.
        external_id (str): The external id.
        name (str): The name of the employee.
        organization_id (int): The id of the organization the employee belongs to.
        organization (Organization): The organization the employee belongs to.
    """

    __tablename__ = "employees"

    external_id: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(200),
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
        back_populates="employees",
    )
