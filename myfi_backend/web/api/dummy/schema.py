from pydantic import BaseModel


class DummyDTO(BaseModel):
    """
    DTO for dummy models.

    It returned when accessing dummy models from the API.
    """

    id: int
    name: str

    class Config:
        orm_mode = True


class DummyInputDTO(BaseModel):
    """DTO for creating new dummy model."""

    name: str
