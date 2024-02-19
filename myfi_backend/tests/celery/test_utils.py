import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.celery.utils import parse_and_save_amc_data
from myfi_backend.db.models.amc_model import AMC  # replace with the actual import


@pytest.mark.anyio
async def test_parse_and_save_amc_data(dbsession: AsyncSession) -> None:
    """Test parsing and saving AMC data."""
    # Mock data
    data = {
        "Table": [
            {
                "amc": "Test AMC",
                "amc_code": "123",
                "add1": "Address 1",
                "add2": "Address 2",
                "add3": "Address 3",
                "email": "test@example.com",
                "phone": "1234567890",
                "webiste": "www.example.com",
                "fund": "Test Fund",
            },
        ],
    }

    # Call the function
    await parse_and_save_amc_data(data, dbsession)
    await dbsession.commit()
    # Get the AMC
    result = await dbsession.execute(select(AMC).where(AMC.code == "123"))
    amc_from_db = result.scalars().first()

    # Assert that the AMC data was inserted correctly
    assert amc_from_db is not None
    assert amc_from_db.name == "Test AMC"
    assert amc_from_db.code == "123"
    assert amc_from_db.address == "Address 1 Address 2 Address 3"
    assert amc_from_db.email == "test@example.com"
    assert amc_from_db.phone == "1234567890"
    assert amc_from_db.website == "www.example.com"
    assert amc_from_db.fund_name == "Test Fund"
