from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """Base model class for database models."""

    __abstract__ = True
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )
