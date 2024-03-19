from typing import Dict

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from pydantic import parse_obj_as

from myfi_backend.db.models.scheme_nav_model import SchemeNAV
from myfi_backend.web.api.scheme.schema import SchemeNavDTO


@pytest.mark.anyio
async def test_get_scheme_nav(
    fastapi_app: FastAPI,
    client: AsyncClient,
    schemenav: SchemeNAV,
) -> None:
    """
    Tests that get_scheme_nav route works.

    :param fastapi_app: current application.
    :param client: client for the app.
    :param schemenav: A SchemeNAV instance for testing.
    """
    url = fastapi_app.url_path_for("get_scheme_nav", scheme_id=schemenav.scheme_id)
    response = await client.get(url)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data["scheme_id"] == str(schemenav.scheme_id)
    assert isinstance(response_data["nav_data"], Dict)
    schemenav_dto = parse_obj_as(SchemeNavDTO, response_data)
    assert schemenav_dto
