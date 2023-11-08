import logging
import os
from typing import Any

from celery import Celery, Task
from celery.schedules import crontab
from myfi_backend.settings import settings

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", settings.celery_broker)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND",
    settings.celery_backend,
)
celery.conf.timezone = "UTC"

celery.autodiscover_tasks()


@celery.task(name="dummy_task")
def dummy_task() -> None:
    """Celery dummy task."""
    logging.info("Received message from Celery!")


@celery.task(name="dummy_scheduled_task")
def dummy_scheduled_task(msg: str) -> None:
    """Celery dummy scheduled task with.

    :param msg: message to the task.

    """
    logging.info(f"Received scheduled message from Celery! with message: {msg}")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Task, **kwargs: Any) -> None:
    """Celery beat scheduler.

    :param sender: Task
    :param kwargs: Any

    """
    # Calls dummy_scheduled_task('hello BEAT') every 10 seconds.
    sender.add_periodic_task(
        10.0,
        dummy_scheduled_task.s("hello BEAT"),
        name="schedule task every 10 seconds",
    )

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        dummy_scheduled_task.s("Happy Mondays!"),
        name="schedule task every Monday at 7:30am",
    )
