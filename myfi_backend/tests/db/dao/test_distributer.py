import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.distributer_dao import DistributorDAO
from myfi_backend.db.models.distributor_model import Distributor
from myfi_backend.db.models.organization_model import Organization


@pytest.mark.anyio
async def test_get_by_id_success(
    dbsession: AsyncSession,
    distributor: Distributor,
) -> None:
    """Test getting a Distributor by id."""
    dao = DistributorDAO(dbsession)
    result = await dao.get_by_id(uuid.UUID(str(distributor.id)))
    assert result is not None


@pytest.mark.anyio
async def test_get_by_id_failure(dbsession: AsyncSession) -> None:
    """Test getting a Distributor by a non-existent id."""
    dao = DistributorDAO(dbsession)
    result = await dao.get_by_id(
        uuid.UUID("00000000-0000-0000-0000-000000000000"),
    )  # non-existent id
    assert result is None


@pytest.mark.anyio
async def test_create_success(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """Test creating a new Distributor."""
    dao = DistributorDAO(dbsession)
    result = await dao.create(
        {
            "name": "New Distributor",
            "external_id": "New External ID",
            "organization_id": uuid.UUID(str(organization.id)),
        },
    )
    assert result is not None
    result_by_id = await dao.get_by_id(uuid.UUID(str(result.id)))
    assert result_by_id is not None
    assert result_by_id.name == "New Distributor"
    assert result_by_id.external_id == "New External ID"
    assert result_by_id.organization_id == organization.id


@pytest.mark.anyio
async def test_update_success(
    dbsession: AsyncSession,
    distributor: Distributor,
) -> None:
    """Test updating a Distributor."""
    dao = DistributorDAO(dbsession)

    # Update the organization
    distributor.name = "Updated Distributor"
    await dao.update(distributor)
    result_by_id = await dao.get_by_id(uuid.UUID(str(distributor.id)))
    assert result_by_id is not None
    assert result_by_id.name == "Updated Distributor"


@pytest.mark.anyio
async def test_get_organization(
    dbsession: AsyncSession,
    distributor: Distributor,
    organization: Organization,
) -> None:
    """Test getting the Organization of a Distributor."""
    dao = DistributorDAO(dbsession)

    # Get the distributor
    distributor_from_db = await dao.get_by_id(uuid.UUID(str(distributor.id)))
    assert distributor_from_db is not None

    # Get the organization of the distributor
    organization_from_db = distributor_from_db.organization
    assert organization_from_db is not None
    assert organization_from_db.id == organization.id
