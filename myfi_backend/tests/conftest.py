import random
import uuid
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, List, Tuple
from unittest.mock import MagicMock, patch

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
from myfi_backend.db.dao.amc_dao import AmcDAO
from myfi_backend.db.dao.distributer_dao import DistributorDAO
from myfi_backend.db.dao.employee_dao import EmployeeDAO
from myfi_backend.db.dao.mutual_fund_scheme_dao import MutualFundSchemeDAO
from myfi_backend.db.dao.organization_dao import OrganizationDAO
from myfi_backend.db.dao.portfolio_dao import PortfolioDAO, PortfolioMutualFundDAO
from myfi_backend.db.dependencies import get_db_session
from myfi_backend.db.models import load_all_models
from myfi_backend.db.models.adviser_model import Adviser
from myfi_backend.db.models.amc_model import AMC
from myfi_backend.db.models.base_model import BaseModel
from myfi_backend.db.models.distributor_model import Distributor
from myfi_backend.db.models.employee_model import Employee
from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme
from myfi_backend.db.models.organization_model import Organization
from myfi_backend.db.models.portfolio_model import Portfolio, PortfolioMutualFund
from myfi_backend.db.utils import create_database, drop_database
from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.settings import settings
from myfi_backend.web.api.otp.schema import OtpDTO, OtpResponseDTO, UserDTO
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
    with patch.object(settings, "db_host", "localhost"):
        target_metadata = BaseModel.metadata
        load_all_models()

        await create_database()

        engine = create_async_engine(str(settings.get_db_url()))
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
    await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        # await trans.rollback()
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


@pytest.fixture
def user_with_email() -> UserDTO:
    """
    Fixture for creating a UserDTO with email.

    :return: UserDTO instance.
    """
    return UserDTO(email="john.doe@example.com")


@pytest.fixture
def user_with_mobile() -> UserDTO:
    """
    Fixture for creating a UserDTO with mobile.

    :return: UserDTO instance.
    """
    return UserDTO(mobile="+919876543210")


@pytest.fixture
@patch("myfi_backend.web.api.otp.views.generate_otp")
async def create_user(
    mock_generate_otp: MagicMock,
    user_with_mobile: UserDTO,
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> uuid.UUID:
    """
    Fixture to create a user in db and return user_id.

    :param user_with_mobile: User data with mobile.
    :param fastapi_app: current application.
    :param client: client for the app.
    :return: user_id of newly created user.

    """
    mock_generate_otp.return_value = "123456"

    # signup, verify, set and verify pin for new users
    signup_url = fastapi_app.url_path_for("signup")
    response = await client.post(
        signup_url,
        json=user_with_mobile.dict(),
    )
    # signup
    user_id = response.json()["user_id"]
    response_ob = OtpResponseDTO.parse_obj(response.json())

    # verify otp
    verify_url = fastapi_app.url_path_for("verify_otp")
    user_with_mobile.user_id = user_id
    otp_data = OtpDTO(user=user_with_mobile, mobile_otp="123456")
    response = await client.post(
        verify_url,
        json=otp_data.dict(),
    )
    response_ob = OtpResponseDTO.parse_obj(response.json())
    return response_ob.user_id


@pytest.fixture
async def amc(dbsession: AsyncSession) -> AMC:
    """
    Fixture for creating an AMC.

    :return: AMC instance written to db.

    """
    amc_dao = AmcDAO(dbsession)
    amc = await amc_dao.create(
        {
            "name": "Test AMC",
            "code": "NEWAMC",
            "address": "New AMC Address",
            "email": "newamc@email.com",
            "phone": "1234567890",
            "website": "https://newamc.com",
            "fund_name": "New AMC Fund",
        },
    )
    await dbsession.commit()
    return amc


@pytest.fixture
async def mutualfundscheme(dbsession: AsyncSession, amc: AMC) -> MutualFundScheme:
    """
    Fixture for creating a MutualFundScheme.

    :return: MutualFundScheme instance written to db.
    """
    mutualfundscheme_dao = MutualFundSchemeDAO(dbsession)
    mutualfundscheme_instance = await mutualfundscheme_dao.create(
        {
            "name": "Test Scheme",
            "amc_id": uuid.UUID(str(amc.id)),
            "scheme_plan": "Test Plan",
            "scheme_type": "Test Type",
            "scheme_category": "Test Category",
            "nav": 10.0,
            "isin": "Test ISIN 2",
            "cagr": 5.0,
            "risk_level": "Test Risk Level",
            "aum": 1000000.0,
            "ter": 1.0,
            "rating": 5,
            "benchmark_index": "Test Benchmark Index",
            "min_investment_sip": 500.0,
            "min_investment_one_time": 5000.0,
            "exit_load": "Test Exit Load",
            "fund_manager": "Test Fund Manager",
            "return_since_inception": 10.0,
            "return_last_year": 5.0,
            "return_last3_years": 15.0,
            "return_last5_years": 25.0,
            "standard_deviation": 0.05,
            "sharpe_ratio": 1.0,
            "sortino_ratio": 1.0,
            "alpha": 0.1,
            "beta": 1.0,
        },
    )
    await dbsession.commit()
    return mutualfundscheme_instance


@pytest.fixture
async def portfolio(dbsession: AsyncSession, adviser: Adviser) -> Portfolio:
    """
    Pytest fixture for creating a PortfolioMutualFund instance.

    :return: Portfolio instance written to db.
    """
    portfolio_dao = PortfolioDAO(dbsession)
    portfolio = await portfolio_dao.create(
        {
            "name": "Test Portfolio",
            "description": "This is a test portfolio",
            "risk_level": "Low",
            "equity_proportion": 40,
            "debt_proportion": 30,
            "hybrid_proportion": 20,
            "gold_proportion": 10,
            "adviser_id": adviser.id,  # Use the adviser fixture to get the adviser id
        },
    )
    await dbsession.commit()
    return portfolio


@pytest.fixture
async def portfolio_mutualfundscheme(
    dbsession: AsyncSession,
    portfolio: Portfolio,
    mutualfundscheme: MutualFundScheme,
) -> PortfolioMutualFund:
    """
    Pytest fixture for creating a PortfolioMutualFund instance.

    It uses the Portfolio and MutualFundScheme fixtures to get the portfolio and mutual
    fund scheme instances.
    It uses the PortfolioMutualFundDAO to create the PortfolioMutualFund instance.

    :return: PortfolioMutualFund instance written to db.
    """
    portfolio_mutualfundscheme_dao = PortfolioMutualFundDAO(dbsession)
    portfolio_mutualfundscheme = await portfolio_mutualfundscheme_dao.create(
        {
            "portfolio_id": portfolio.id,
            "mutualfundscheme_id": mutualfundscheme.id,
            "proportion": 100,
        },
    )
    await dbsession.commit()
    return portfolio_mutualfundscheme


@pytest.fixture
async def mutualfundscheme_factory(
    dbsession: AsyncSession,
    amc: AMC,
) -> Callable[[], Awaitable[MutualFundScheme]]:
    """
    Pytest fixture for creating a MutualFundScheme instance.

    It returns a function that creates a new MutualFundScheme instance.

    :return: Function that creates a MutualFundScheme instance.
    """

    async def _mutualfundscheme_factory() -> MutualFundScheme:
        mutualfundscheme_dao = MutualFundSchemeDAO(dbsession)
        mutualfundscheme_instance = await mutualfundscheme_dao.create(
            {
                "name": f"Test Scheme {str(uuid.uuid4())[:12]}",  # noqa: WPS237
                "amc_id": uuid.UUID(str(amc.id)),
                "scheme_plan": "Test Plan",
                "scheme_type": "Test Type",
                "scheme_category": "Test Category",
                "nav": 10.0,
                "isin": f"{str(uuid.uuid4())[:12]}",  # noqa: WPS237
                "cagr": 5.0,
                "risk_level": "Test Risk Level",
                "aum": 1000000.0,
                "ter": 1.0,
                "rating": 5,
                "benchmark_index": "Test Benchmark Index",
                "min_investment_sip": 500.0,
                "min_investment_one_time": 5000.0,
                "exit_load": "Test Exit Load",
                "fund_manager": "Test Fund Manager",
                "return_since_inception": 10.0,
                "return_last_year": 5.0,
                "return_last3_years": 15.0,
                "return_last5_years": 25.0,
                "standard_deviation": 0.05,
                "sharpe_ratio": 1.0,
                "sortino_ratio": 1.0,
                "alpha": 0.1,
                "beta": 1.0,
            },
        )
        await dbsession.commit()
        return mutualfundscheme_instance

    return _mutualfundscheme_factory


@pytest.fixture
def mutualfundschemes_factory(  # noqa: WPS234
    mutualfundscheme_factory: Callable[
        [],
        Coroutine[
            Any,
            Any,
            MutualFundScheme,
        ],
    ],
    dbsession: AsyncSession,
    amc: AMC,
) -> Callable[[int], Coroutine[Any, Any, List[MutualFundScheme]]]:
    """
    Pytest fixture for creating a list of MutualFundScheme instances.

    It uses the MutualFundScheme fixture to get the mutual fund scheme instance.
    It returns a function that takes a parameter n and creates n MutualFundScheme
    instances.

    :return: Function that creates a list of n MutualFundScheme instances.
    """

    async def _mutualfundschemes_factory(num_schemes: int) -> List[MutualFundScheme]:
        mutualfundschemes = []
        for _ in range(num_schemes):
            mutualfundscheme_instance = await mutualfundscheme_factory()
            mutualfundschemes.append(mutualfundscheme_instance)
        return mutualfundschemes

    return _mutualfundschemes_factory


@pytest.fixture
def mutualfundschemes_with_proportions_factory(  # noqa: WPS234
    mutualfundschemes_factory: Callable[
        [int],
        Coroutine[Any, Any, List[MutualFundScheme]],
    ],
) -> Callable[[int], Coroutine[Any, Any, List[Tuple[MutualFundScheme, int]]]]:
    """
    Create a factory for creating a list of mutual fund schemes with proportions.

    The proportions are random and add up to 100.

    :param mutualfundschemes_factory: Factory that create MutualFundScheme instances.
    :return: Factory that creates a list of MutualFundScheme+proportion instances.
    """

    async def _mutualfundschemes_with_proportions_factory(
        num_schemes: int,
    ) -> List[Tuple[MutualFundScheme, int]]:
        mutualfundschemes = await mutualfundschemes_factory(num_schemes)
        proportions = [random.random() for _ in range(num_schemes)]  # noqa: S311
        sum_proportions = sum(proportions)
        proportions = [
            round(100 * (proportion / sum_proportions)) for proportion in proportions
        ]
        # Adjust the last proportion so that the proportions add up to 100
        proportions[-1] = 100 - sum(proportions[:-1])
        return list(
            zip(mutualfundschemes, [int(proportion) for proportion in proportions]),
        )

    return _mutualfundschemes_with_proportions_factory
