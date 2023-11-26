from datetime import datetime

from pydantic import BaseModel


class InvestmentValueDTO(BaseModel):
    """Represents the value of an investment at a specific point in time.

    Attributes:
        value (float): The value of the investment.
        date (datetime): The date of the investment value.
    """

    value: float
    date: datetime
