import uuid
from typing import Any, AsyncGenerator

import pytest
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from myfi_backend.db.dao.adviser_dao import AdviserDAO
from myfi_backend.db.dao.distributer_dao import DistributorDAO
from myfi_backend.db.dao.employee_dao import EmployeeDAO
from myfi_backend.db.dao.organization_dao import OrganizationDAO
from myfi_backend.db.dependencies import get_db_session
from myfi_backend.db.models import load_all_models
from myfi_backend.db.models.adviser_model import Adviser
from myfi_backend.db.models.base_model import BaseModel
from myfi_backend.db.models.distributer_model import Distributor
from myfi_backend.db.models.employee_model import Employee
from myfi_backend.db.models.organization_model import Organization
from myfi_backend.db.utils import create_database, drop_database
from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.settings import settings
from myfi_backend.web.application import get_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    target_metadata = BaseModel.metadata
    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(target_metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def organization(dbsession: AsyncSession) -> Organization:
    """
    Fixture for creating an Organization instance.

    :return: Organization written to db.
    """
    dao = OrganizationDAO(dbsession)
    organization = await dao.create(
        {
            "name": "New Organization",
            "description": "New Description",
        },
    )
    await dbsession.commit()
    return organization


@pytest.fixture
async def distributor(
    dbsession: AsyncSession,
    organization: Organization,
) -> Distributor:
    """
    Fixture for creating a Distributor instance.

    :return: Distributor instance written to db.
    """
    dao = DistributorDAO(dbsession)
    distributor = await dao.create(
        {
            "name": "Test Distributer",
            "external_id": "Test external id",
            "organization_id": uuid.UUID(str(organization.id)),
        },
    )
    await dbsession.commit()
    return distributor


@pytest.fixture
async def adviser(
    dbsession: AsyncSession,
    organization: Organization,
) -> Adviser:
    """
    Fixture for creating a Distributor instance.

    :return: Adviser instance written to db.
    """
    dao = AdviserDAO(dbsession)
    adviser = await dao.create(
        {
            "name": "Test Adviser",
            "external_id": "Test external id",
            "organization_id": uuid.UUID(str(organization.id)),
        },
    )
    await dbsession.commit()
    return adviser


@pytest.fixture
async def employee(
    dbsession: AsyncSession,
    organization: Organization,
) -> Employee:
    """
    Fixture for creating a Employee instance.

    :return: Employee instance written to db.
    """
    dao = EmployeeDAO(dbsession)
    employee = await dao.create(
        {
            "name": "Test employee",
            "external_id": "Test external id",
            "organization_id": uuid.UUID(str(organization.id)),
        },
    )
    await dbsession.commit()
    return employee
