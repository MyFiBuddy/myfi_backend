from datetime import datetime, timedelta
from random import choice
from typing import List
from uuid import UUID

from myfi_backend.web.api.investment.schema import InvestmentValueDTO


def get_investment_values(user_id: UUID) -> List[InvestmentValueDTO]:
    """
    Generates random investment values for a user over the last 3 months.

    :param user_id: The UUID of the user.
    :return: A list of InvestmentValueDTO instances representing the user's investment \
    values over the last 3 months.

    """
    # Start with a value of 100
    value = 100.0

    # Generate investment values for the last 3 months
    investment_value_dtos = []
    for index in range(90):
        date = datetime.now() - timedelta(days=index)

        # Increase or decrease the value by 5
        value += choice([-5, 5])  # noqa: S311

        # Ensure the value stays between 100 and 1000
        value = max(100, min(value, 1000))

        investment_value_dtos.append(InvestmentValueDTO(value=value, date=date))

    return investment_value_dtos
