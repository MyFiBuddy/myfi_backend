from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from myfi_backend.db.models.base_model import BaseModel


class Dummy(BaseModel):
    """Model for demo purpose."""

    __tablename__ = "dummy_model"

    name: Mapped[str] = mapped_column(
        String(length=200),
        unique=True,
        index=True,
        nullable=False,
    )
