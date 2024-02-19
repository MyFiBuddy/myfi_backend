import asyncio
import logging
import os
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from celery import Celery, Task
from celery.schedules import crontab
from myfi_backend.celery.utils import parse_and_save_amc_data
from myfi_backend.services.api.accord_client import AmcClient
from myfi_backend.settings import settings

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", settings.celery_broker)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND",
    settings.celery_backend,
)
celery.conf.timezone = "UTC"

celery.autodiscover_tasks()

accord_token = settings.accord_token
accord_base_url = settings.accord_base_url

engine = create_async_engine(str(settings.get_db_url()), echo=settings.db_echo)
session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


def get_db_session() -> AsyncSession:
    """
    Create and get database session.

    :return: database session.
    """
    return session_factory()


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


@celery.task(name="fetch_amc_data_task")
def fetch_amc_data_task() -> None:
    """Celery task to fetch AMC data."""
    client = AmcClient(accord_base_url)
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Amc_mst",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )
    dbsession = get_db_session()
    loop.run_until_complete(parse_and_save_amc_data(data, dbsession))
    logging.info("Fetched and saved AMC data to the database.")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Task, **kwargs: Any) -> None:
    """Celery beat scheduler.

    :param sender: Task
    :param kwargs: Any

    """
    # Calls dummy_scheduled_task('hello BEAT') every 5 mins.
    sender.add_periodic_task(
        5 * 60,
        dummy_scheduled_task.s("hello BEAT"),
        name="schedule task every 10 seconds",
    )

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        dummy_scheduled_task.s("Happy Mondays!"),
        name="schedule task every Monday at 7:30am",
    )

    # Calls fetch_amc_data_task() every day at 6 AM.
    sender.add_periodic_task(
        crontab(hour=6, minute=0),
        fetch_amc_data_task.s(),
        name="Fetch AMC data every day at 6 AM",
    )
