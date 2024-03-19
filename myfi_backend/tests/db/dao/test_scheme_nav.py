import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.scheme_nav_dao import SchemeNavDAO
from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme
from myfi_backend.db.models.scheme_nav_model import SchemeNAV


@pytest.mark.anyio
async def test_get_by_scheme_id_success(
    dbsession: AsyncSession,
    schemenav: SchemeNAV,
) -> None:
    """Test getting a SchemeNAV by scheme_id."""
    dao = SchemeNavDAO(dbsession)
    result = await dao.get_by_scheme_id(uuid.UUID(str(schemenav.scheme_id)))
    assert result is not None


@pytest.mark.anyio
async def test_get_by_scheme_id_failure(dbsession: AsyncSession) -> None:
    """Test getting a SchemeNAV by a non-existent scheme_id."""
    dao = SchemeNavDAO(dbsession)
    result = await dao.get_by_scheme_id(
        uuid.UUID("00000000-0000-0000-0000-000000000000"),
    )  # non-existent scheme_id
    assert result is None


@pytest.mark.anyio
async def test_create_success(
    mutualfundscheme: MutualFundScheme,
    dbsession: AsyncSession,
) -> None:
    """Test creating a new SchemeNAV."""
    dao = SchemeNavDAO(dbsession)
    result = await dao.create(
        {
            "scheme_id": mutualfundscheme.id,
            "nav_data": {"2022-01-01": 10.0},
        },
    )
    assert result is not None
    result_by_id = await dao.get_by_scheme_id(uuid.UUID(str(result.scheme_id)))
    assert result_by_id is not None
    assert result_by_id.nav_data == {"2022-01-01": 10.0}  # type: ignore


@pytest.mark.anyio
async def test_update_success(
    dbsession: AsyncSession,
    schemenav: SchemeNAV,
) -> None:
    """Test updating a SchemeNAV."""
    dao = SchemeNavDAO(dbsession)
    schemenav.nav_data = {"2022-01-02": 20.0}  # type: ignore
    await dao.update(schemenav)
    result = await dao.get_by_scheme_id(uuid.UUID(str(schemenav.scheme_id)))
    assert result is not None
    assert result.nav_data == {"2022-01-02": 20.0}  # type: ignore


@pytest.mark.anyio
async def test_upsert_success(
    dbsession: AsyncSession,
    schemenav: SchemeNAV,
) -> None:
    """Test upserting a SchemeNAV."""
    dao = SchemeNavDAO(dbsession)
    new_nav_data = {"2022-01-03": 30.0, "2023-01-03": 30.0}
    await dao.upsert(
        {
            "scheme_id": schemenav.scheme_id,
            "nav_data": new_nav_data,
        },
    )

    # Retrieve the updated SchemeNAV from the database
    result = await dao.get_by_id(schemenav.id)

    assert result is not None
    for item in new_nav_data.items():
        assert item in result.nav_data.items()  # type: ignore


@pytest.mark.anyio
async def test_add_latest_nav_success(
    dbsession: AsyncSession,
    schemenav: SchemeNAV,
) -> None:
    """Test adding the latest NAV to a SchemeNAV."""
    dao = SchemeNavDAO(dbsession)
    await dao.add_latest_nav(schemenav.scheme_id, "2022-01-04", 40.0)

    # Retrieve the updated SchemeNAV from the database
    await dao.get_by_id(schemenav.id)

    # Retrieve the updated SchemeNAV from the database
    result = await dao.get_by_id(schemenav.id)

    assert result is not None
    assert ("2022-01-04", 40.0) in result.nav_data.items()  # type: ignore
    for item in schemenav.nav_data.items():  # type: ignore
        assert item in result.nav_data.items()  # type: ignore
