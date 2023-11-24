import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.adviser_dao import AdviserDAO
from myfi_backend.db.models.adviser_model import Adviser
from myfi_backend.db.models.organization_model import Organization


@pytest.mark.anyio
async def test_get_by_id_success(
    dbsession: AsyncSession,
    adviser: Adviser,
) -> None:
    """
    Test getting an Adviser by id.

    :param dbsession: Database session to use for the test.
    :param adviser: The Adviser instance to get.
    """
    dao = AdviserDAO(dbsession)
    result = await dao.get_by_id(uuid.UUID(str(adviser.id)))
    assert result is not None


@pytest.mark.anyio
async def test_get_by_id_failure(dbsession: AsyncSession) -> None:
    """
    Test getting an Adviser by a non-existent id.

    :param dbsession: Database session to use for the test.
    """
    dao = AdviserDAO(dbsession)
    result = await dao.get_by_id(
        uuid.UUID("00000000-0000-0000-0000-000000000000"),
    )  # non-existent id
    assert result is None


@pytest.mark.anyio
async def test_create_success(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """
    Test creating an Adviser.

    :param dbsession: Database session to use for the test.
    :param organization: The Organization instance to associate with the Adviser.
    """
    dao = AdviserDAO(dbsession)
    result = await dao.create(
        {
            "name": "Adviser 1",
            "external_id": "external_id_1",
            "organization_id": uuid.UUID(str(organization.id)),
        },
    )
    assert result is not None
    result_by_id = await dao.get_by_id(uuid.UUID(str(result.id)))
    assert result_by_id is not None
    assert result_by_id.name == "Adviser 1"
    assert result_by_id.external_id == "external_id_1"
    assert result_by_id.organization_id == organization.id


@pytest.mark.anyio
async def test_update_success(
    dbsession: AsyncSession,
    adviser: Adviser,
) -> None:
    """
    Test updating an Adviser.

    :param dbsession: Database session to use for the test.
    :param adviser: The Adviser instance to update.
    """
    dao = AdviserDAO(dbsession)
    adviser.name = "Updated Adviser"
    await dao.update(adviser)
    result_by_id = await dao.get_by_id(uuid.UUID(str(adviser.id)))
    assert result_by_id is not None
    assert result_by_id.name == "Updated Adviser"


@pytest.mark.anyio
async def test_get_organization(
    dbsession: AsyncSession,
    adviser: Adviser,
    organization: Organization,
) -> None:
    """
    Test getting the Organization of an Adviser.

    :param dbsession: Database session to use for the test.
    :param adviser: The Adviser instance to get the Organization of.
    """
    dao = AdviserDAO(dbsession)

    # Get the distributor
    adviser_from_db = await dao.get_by_id(uuid.UUID(str(adviser.id)))
    assert adviser_from_db is not None

    # Get the organization of the distributor
    organization_from_db = adviser_from_db.organization
    assert organization_from_db is not None
    assert organization_from_db.id == organization.id
