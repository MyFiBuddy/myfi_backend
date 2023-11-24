# dao/test_employee.py
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.employee_dao import EmployeeDAO
from myfi_backend.db.models.employee_model import Employee
from myfi_backend.db.models.organization_model import Organization


@pytest.mark.anyio
async def test_get_by_id_success(
    dbsession: AsyncSession,
    employee: Employee,
) -> None:
    """
    Test getting an Employee by id.

    :param dbsession: Database session to use for the test.
    :param employee: Employee fixture.
    """
    dao = EmployeeDAO(dbsession)
    result = await dao.get_by_id(uuid.UUID(str(employee.id)))
    assert result is not None
    assert result.id == employee.id


@pytest.mark.anyio
async def test_get_by_external_id_success(
    dbsession: AsyncSession,
    employee: Employee,
) -> None:
    """
    Test getting an Employee by external id.

    :param dbsession: Database session to use for the test.
    :param employee: Employee fixture.
    """
    dao = EmployeeDAO(dbsession)
    result = await dao.get_by_external_id(employee.external_id)
    assert result is not None
    assert result.external_id == employee.external_id


@pytest.mark.anyio
async def test_create_success(
    dbsession: AsyncSession,
    organization: Organization,
) -> None:
    """
    Test creating an Employee.

    :param dbsession: Database session to use for the test.
    :param organization: Organization fixture.
    """
    dao = EmployeeDAO(dbsession)
    result = await dao.create(
        {
            "name": "name",
            "external_id": "external_id",
            "organization_id": uuid.UUID(str(organization.id)),
        },
    )
    assert result is not None
    result_by_id = await dao.get_by_id(uuid.UUID(str(result.id)))
    assert result_by_id is not None
    assert result_by_id.name == "name"
    assert result_by_id.external_id == "external_id"
    assert result_by_id.organization_id == organization.id


@pytest.mark.anyio
async def test_update_success(
    dbsession: AsyncSession,
    employee: Employee,
) -> None:
    """
    Test updating an existing Employee.

    :param dbsession: Database session to use for the test.
    :param employee: Employee fixture.
    """
    dao = EmployeeDAO(dbsession)
    employee.name = "new_name"
    employee.external_id = "new_external_id"
    updated_employee = await dao.update(employee)
    assert updated_employee is not None
    assert updated_employee.name == "new_name"
    assert updated_employee.external_id == "new_external_id"


@pytest.mark.anyio
async def test_delete(
    dbsession: AsyncSession,
    employee: Employee,
) -> None:
    """
    Test deleting an Employee.

    :param dbsession: Database session to use for the test.
    """
    dao = EmployeeDAO(dbsession)
    employee_by_id = await dao.get_by_id(uuid.UUID(str(employee.id)))
    assert employee_by_id is not None
    employee_id = employee_by_id.id
    await dao.delete(uuid.UUID(str(employee_id)))
    deleted_employee = await dao.get_by_id(uuid.UUID(str(employee_id)))
    assert deleted_employee is None


@pytest.mark.anyio
async def test_get_by_id_failure(
    dbsession: AsyncSession,
    employee: Employee,
) -> None:
    """
    Test getting an Employee by a non-existent id.

    :param dbsession: Database session to use for the test.
    :param employee: Employee fixture.
    """
    dao = EmployeeDAO(dbsession)
    result = await dao.get_by_id(
        uuid.UUID("00000000-0000-0000-0000-000000000000"),
    )  # Assuming 9999 is a non-existent id
    assert result is None


@pytest.mark.anyio
async def test_get_by_external_id_failure(
    dbsession: AsyncSession,
    employee: Employee,
) -> None:
    """
    Test getting an Employee by a non-existent external id.

    :param dbsession: Database session to use for the test.
    :param employee: Employee fixture.
    """
    dao = EmployeeDAO(dbsession)
    result = await dao.get_by_external_id("non_existent_external_id")
    assert result is None


@pytest.mark.anyio
async def test_get_organization(
    dbsession: AsyncSession,
    employee: Employee,
    organization: Organization,
) -> None:
    """
    Test getting the Organization of an Employee.

    :param dbsession: Database session to use for the test.
    :param employee: The Employee instance to get the Organization of.
    """
    dao = EmployeeDAO(dbsession)

    # Get the employee
    employee_from_db = await dao.get_by_id(uuid.UUID(str(employee.id)))
    assert employee_from_db is not None

    # Get the organization of the employee
    organization_from_db = employee_from_db.organization
    assert organization_from_db is not None
    assert organization_from_db.id == organization.id
