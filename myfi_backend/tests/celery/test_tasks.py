from unittest.mock import MagicMock, patch

import pytest

from myfi_backend.celery.tasks import (
    dummy_scheduled_task,
    dummy_task,
    fetch_amc_data_task,
)


@patch("myfi_backend.celery.tasks.logging")
def test_dummy_task(mock_logging: MagicMock) -> None:
    """Test the dummy_task.

    Test function by calling it and checking if it logs the expected message.
    """
    dummy_task.apply()
    mock_logging.info.assert_called_once_with("Received message from Celery!")


@patch("myfi_backend.celery.tasks.logging")
def test_dummy_scheduled_task(mock_logging: MagicMock) -> None:
    """Test test_dummy_scheduled_task.

    Test to check if the Celery task 'dummy_scheduled_task' is working as expected.
    """
    msg: str = "Hello, world!"
    dummy_scheduled_task.apply(args=[msg])
    mock_logging.info.assert_called_once_with(
        f"Received scheduled message from Celery! with message: {msg}",
    )


@patch("myfi_backend.celery.tasks.logging")
@patch("myfi_backend.celery.tasks.AmcClient")
@patch("myfi_backend.celery.tasks.asyncio.run", new_callable=MagicMock)
@patch("myfi_backend.celery.tasks.accord_base_url", new_callable=MagicMock)
@pytest.mark.anyio
async def test_fetch_amc_data_task(
    mock_url: MagicMock,
    mock_run: MagicMock,
    mock_amc_client: MagicMock,
    mock_logging: MagicMock,
) -> None:
    """Test fetch_amc_data_task.

    Test to check if the Celery task 'fetch_amc_data_task' is working as expected.
    """
    mock_client_instance = mock_amc_client.return_value

    fetch_amc_data_task()

    mock_amc_client.assert_called_once_with(mock_url)
    mock_run.assert_any_call(
        mock_client_instance.fetch_amc_data(  # noqa: S106
            filename="Amc_mst",
            date="30092022",
            section="MFMaster",
            sub="",
            token="",
        ),
    )
    mock_logging.info.assert_called_once_with(
        "Fetched and saved AMC data to the database.",
    )
