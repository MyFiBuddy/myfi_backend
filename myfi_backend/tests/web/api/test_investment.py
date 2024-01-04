import uuid
from typing import List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import parse_obj_as
from starlette import status

from myfi_backend.web.api.investment.schema import InvestmentValueDTO


@pytest.mark.anyio
async def test_user_investment_value_success(
    create_user: uuid.UUID,
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """
    Fixture to create a user in db and return user_id.

    :param create_user: Fixture to create a new user.
    :param fastapi_app: current application.
    :param client: client for the app.

    """
    # get investment value for an existing user
    signup_url = fastapi_app.url_path_for("user_investment_value")
    response = await client.get(
        signup_url,
        params={"user_id": str(create_user)},
    )

    # check that the value is returned successfully
    assert response
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    investments = parse_obj_as(List[InvestmentValueDTO], response_data)
    assert investments


@pytest.mark.anyio
async def test_user_investment_value_failure(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """
    Fixture to create a user in db and return user_id.

    :param fastapi_app: current application.
    :param client: client for the app.

    """
    # get investment value for a non existent user
    signup_url = fastapi_app.url_path_for("user_investment_value")
    response = await client.get(
        signup_url,
        params={"user_id": str(uuid.uuid4())},
    )
    # check that the call is failed
    assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid request."
