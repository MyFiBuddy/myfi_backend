from typing import Any, Dict

from myfi_backend.services.api.http_client import HttpClient


class AmcClient(HttpClient):
    """AmcClient client for fetching AMC data."""

    async def fetch_amc_data(  # noqa: WPS211
        self,
        filename: str,
        date: str,
        section: str,
        sub: str,
        token: str,
    ) -> Dict[str, Any]:
        """
        Fetch AMC data from the API.

        :param filename: Filename parameter for the API request.
        :param date: Date parameter for the API request.
        :param section: Section parameter for the API request.
        :param sub: Sub parameter for the API request.
        :param token: Token parameter for the API request.
        :return: Parsed JSON response from the API.
        """
        params = {
            "filename": filename,
            "date": date,
            "section": section,
            "sub": sub,
            "token": token,
        }
        return await self.fetch_data("GetRawDataJSON", params)

    async def fetch_amc_scheme_data(  # noqa: WPS211
        self,
        filename: str,
        date: str,
        section: str,
        sub: str,
        token: str,
    ) -> Dict[str, Any]:
        """
        Fetch AMC data from the API.

        :param filename: Filename parameter for the API request.
        :param date: Date parameter for the API request.
        :param section: Section parameter for the API request.
        :param sub: Sub parameter for the API request.
        :param token: Token parameter for the API request.
        :return: Parsed JSON response from the API.
        """
        params = {
            "filename": filename,
            "date": date,
            "section": section,
            "sub": sub,
            "token": token,
        }
        return await self.fetch_data("GetRawDataJSON", params)
