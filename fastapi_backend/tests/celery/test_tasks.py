from unittest.mock import MagicMock, patch

from fastapi_backend.celery.tasks import dummy_scheduled_task, dummy_task


@patch("fastapi_backend.celery.tasks.logging")
def test_dummy_task(mock_logging: MagicMock) -> None:
    """Test the dummy_task.

    Test function by calling it and checking if it logs the expected message.
    """
    dummy_task.apply()
    mock_logging.info.assert_called_once_with("Received message from Celery!")


@patch("fastapi_backend.celery.tasks.logging")
def test_dummy_scheduled_task(mock_logging: MagicMock) -> None:
    """Test test_dummy_scheduled_task.

    Test to check if the Celery task 'dummy_scheduled_task' is working as expected.
    """
    msg: str = "Hello, world!"
    dummy_scheduled_task.apply(args=[msg])
    mock_logging.info.assert_called_once_with(
        f"Received scheduled message from Celery! with message: {msg}",
    )
