from typing import Dict
from uuid import UUID

from pydantic import BaseModel


class SchemeDTO(BaseModel):
    """DTO for mutual fund schemes."""

    scheme_id: UUID
    scheme_name: str
    one_year_return: float
    three_year_return: float
    five_year_return: float


class SchemeNavDTO(BaseModel):
    """DTO for mutual fund scheme NAVs."""

    scheme_id: UUID
    nav_data: Dict[str, float]
