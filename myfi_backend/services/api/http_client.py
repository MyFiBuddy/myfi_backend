from typing import Any, Dict

import httpx


class HttpClient:
    """
    Generic HTTP client to handle requests to APIs.

    :param base_url: The base URL for the API.
    :type base_url: str
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from the API.

        :param endpoint: API endpoint to fetch data from.
        :param params: Query parameters to include in the request.
        :return: Parsed JSON response from the API.
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/{endpoint}"
            response = await client.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Parse the JSON response and return it
