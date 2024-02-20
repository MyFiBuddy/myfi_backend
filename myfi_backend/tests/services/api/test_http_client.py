from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response

from myfi_backend.services.api.http_client import HttpClient


@pytest.mark.anyio
async def test_fetch_data() -> None:
    """Test fetch_data method."""
    # Mock data
    base_url = "http://test.com"
    endpoint = "test_endpoint"
    params = {"key": "value"}
    api_response = {"data": "Test data"}

    # Create HttpClient object
    http_client = HttpClient(base_url)

    # Mock httpx.AsyncClient.get method
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock(spec=Response, status_code=200)
        mock_response.json = AsyncMock(return_value=api_response)
        mock_get.return_value = mock_response

        # Call the function
        result = await http_client.fetch_data(endpoint, params)

        # Assert that get was called with correct parameters
        mock_get.assert_called_once_with(f"{base_url}/{endpoint}", params=params)

        # Assert that the function returned the correct result
        assert result == api_response
