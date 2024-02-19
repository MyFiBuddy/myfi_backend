from unittest.mock import AsyncMock, patch

import pytest

from myfi_backend.services.api.accord_client import AmcClient


@pytest.mark.anyio
async def test_fetch_amc_data() -> None:
    """Test fetch_amc_data method."""
    # Mock data
    filename = "test_filename"
    date = "2022-01-01"
    section = "test_section"
    sub = "test_sub"
    token = "test_token"  # noqa: S105
    api_response = {"Table": "Test data"}

    # Create AmcClient object
    amc_client = AmcClient("test_base_url")

    # Use patch to replace the fetch_data method with a mock
    with patch.object(
        amc_client,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch_data:
        mock_fetch_data.return_value = api_response

        # Call the function
        result = await amc_client.fetch_amc_data(filename, date, section, sub, token)

        # Assert that fetch_data was called with correct parameters
        mock_fetch_data.assert_called_once_with(
            "GetRawDataJSON",
            {
                "filename": filename,
                "date": date,
                "section": section,
                "sub": sub,
                "token": token,
            },
        )

        # Assert that the function returned the correct result
        assert result == api_response
