import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from myfi_backend.db.dao.adviser_dao import AdviserDAO
from myfi_backend.db.dao.distributer_dao import DistributorDAO
from myfi_backend.db.dao.employee_dao import EmployeeDAO
from myfi_backend.db.dao.organization_dao import OrganizationDAO
from myfi_backend.db.models.organization_model import Organization


@pytest.mark.anyio
async def test_get_by_id_success(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """Test getting an Organization by id."""
    dao = OrganizationDAO(dbsession)
    result = await dao.get_by_id(uuid.UUID(str(organization.id)))
    assert result is not None


@pytest.mark.anyio
async def test_get_by_id_failure(dbsession: AsyncSession) -> None:
    """Test getting an Organization by a non-existent id."""
    dao = OrganizationDAO(dbsession)
    result = await dao.get_by_id(
        uuid.UUID("00000000-0000-0000-0000-000000000000"),
    )  # non-existent id
    assert result is None


@pytest.mark.anyio
async def test_create_success(dbsession: AsyncSession) -> None:
    """Test creating a new Organization."""
    dao = OrganizationDAO(dbsession)
    result = await dao.create(
        {
            "name": "New Organization",
            "description": "New Description",
        },
    )
    assert result is not None
    assert result.id is not None
    result_by_id = await dao.get_by_id(uuid.UUID(str(result.id)))
    assert result_by_id is not None
    assert result_by_id.name == "New Organization"
    assert result_by_id.description == "New Description"


@pytest.mark.anyio
async def test_update_success(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """Test updating an Organization."""
    dao = OrganizationDAO(dbsession)

    # Retrieve the created organization
    retrieved_organization = await dao.get_by_id(uuid.UUID(str(organization.id)))
    assert retrieved_organization is not None

    # Update the organization
    retrieved_organization.name = "Updated Organization"
    retrieved_organization.description = "Updated Description"
    updated_organization = await dao.update(retrieved_organization)
    assert updated_organization is not None
    assert updated_organization.id == retrieved_organization.id
    assert updated_organization.name == retrieved_organization.name
    assert updated_organization.description == retrieved_organization.description


@pytest.mark.anyio
async def test_get_distributors(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """Test getting the Distributors of an Organization."""
    distributor_dao = DistributorDAO(dbsession)

    # Create distributors for the organization
    distributors = [
        await distributor_dao.create(
            {
                "name": "Distributor 1",
                "organization_id": uuid.UUID(str(organization.id)),
            },
        ),
        await distributor_dao.create(
            {
                "name": "Distributor 2",
                "organization_id": uuid.UUID(str(organization.id)),
            },
        ),
    ]

    # Get the organization
    result = await dbsession.execute(
        select(Organization)
        .where(Organization.id == organization.id)
        .options(
            selectinload(Organization.distributors),
        ),
    )
    organization_from_db = result.scalars().first()
    assert organization_from_db is not None

    # Get the distributors of the organization
    distributors_from_db = organization_from_db.distributors
    assert distributors_from_db is not None
    assert len(distributors_from_db) == len(distributors)
    assert distributors_from_db[0].id == distributors[0].id
    assert distributors_from_db[1].id == distributors[1].id


@pytest.mark.anyio
async def test_get_advisers(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """Test getting the Distributors of an Organization."""
    adviser_dao = AdviserDAO(dbsession)

    # Create advisers for the organization
    advisers = [
        await adviser_dao.create(
            {
                "name": "Distributor 1",
                "organization_id": uuid.UUID(str(organization.id)),
            },
        ),
        await adviser_dao.create(
            {
                "name": "Distributor 2",
                "organization_id": uuid.UUID(str(organization.id)),
            },
        ),
    ]

    # Get the organization
    result = await dbsession.execute(
        select(Organization)
        .where(Organization.id == organization.id)
        .options(
            selectinload(Organization.advisers),
        ),
    )
    organization_from_db = result.scalars().first()
    assert organization_from_db is not None

    # Get the distributors of the organization
    advisers_from_db = organization_from_db.advisers
    assert advisers_from_db is not None
    assert len(advisers_from_db) == len(advisers)
    assert advisers_from_db[0].id == advisers[0].id
    assert advisers_from_db[1].id == advisers[1].id


@pytest.mark.anyio
async def test_get_employees(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """Test getting the Employees of an Organization."""
    employee_dao = EmployeeDAO(dbsession)

    # Create employee for the organization
    employees = [
        await employee_dao.create(
            {
                "name": "Employee 1",
                "organization_id": uuid.UUID(str(organization.id)),
            },
        ),
        await employee_dao.create(
            {
                "name": "Employee 2",
                "organization_id": uuid.UUID(str(organization.id)),
            },
        ),
    ]

    # Get the organization
    result = await dbsession.execute(
        select(Organization)
        .where(Organization.id == organization.id)
        .options(
            selectinload(Organization.employees),
        ),
    )
    organization_from_db = result.scalars().first()
    assert organization_from_db is not None

    # Get the employees of the organization
    employees_from_db = organization_from_db.employees
    assert employees_from_db is not None
    assert len(employees_from_db) == len(employees)
    assert employees_from_db[0].id == employees[0].id
    assert employees_from_db[1].id == employees[1].id
