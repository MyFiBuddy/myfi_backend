from asyncio import AbstractEventLoop
from unittest.mock import MagicMock, patch

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


def test_fetch_amc_data_task() -> None:
    """Test fetch_amc_data_task.

    Test to check if the Celery task 'fetch_amc_data_task' is working as expected.
    """
    with patch(  # noqa: WPS316
        "myfi_backend.celery.tasks.AmcClient",
    ) as mock_amc_client, patch(
        "myfi_backend.celery.tasks.accord_base_url",
        new_callable=MagicMock,
    ) as mock_url, patch(
        "myfi_backend.celery.tasks.accord_token",
        new="test_token",
    ) as mock_accord_token, patch(
        "myfi_backend.celery.tasks.parse_and_save_amc_data",
        new_callable=MagicMock,
    ) as mock_parse_and_save, patch(
        "asyncio.get_event_loop",
    ) as mock_get_event_loop:
        mock_loop = MagicMock(spec=AbstractEventLoop)
        mock_get_event_loop.return_value = mock_loop

        mock_client_instance = mock_amc_client.return_value
        mock_client_instance.fetch_amc_data = MagicMock()

        fetch_amc_data_task.apply()

        mock_amc_client.assert_called_once_with(mock_url)
        mock_parse_and_save.assert_called_once()
        mock_client_instance.fetch_amc_data.assert_called_once_with(
            filename="Amc_mst",
            date="30092022",
            section="MFMaster",
            sub="",
            token=mock_accord_token,
        )
