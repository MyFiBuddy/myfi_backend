# flake8: noqa
import asyncio
import logging
import os
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from celery import Celery, Task
from celery.schedules import crontab
from myfi_backend.celery.utils import (
    insert_dummy_data,
    parse_and_save_amc_data,
    parse_and_save_scheme_data,
)
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
    loop = (
        asyncio.get_event_loop()
        if asyncio.get_event_loop()
        else asyncio.new_event_loop()
    )
    asyncio.set_event_loop(loop)
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


@celery.task(name="fetch_amc_scheme_task")
def fetch_amc_scheme_data_task() -> None:
    """Celery task to fetch AMC scheme data."""
    client = AmcClient(accord_base_url)
    loop = (
        asyncio.get_event_loop()
        if asyncio.get_event_loop()
        else asyncio.new_event_loop()
    )
    asyncio.set_event_loop(loop)
    data_scheme = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Scheme_Details",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_aum = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Scheme_paum",
            date="30092022",
            section="MFPortfolio",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_classcode = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Sclass_mst",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_plan = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Plan_mst",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_risk_level = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Scheme_master",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_nav_return = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Mf_abs_return",
            date="30092022",
            section="MFNav",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_exit_load = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Schemeload",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_ratio = loop.run_until_complete(
        client.fetch_amc_data(
            filename="MF_Ratios_DefaultBM",
            date="30092022",
            section="MFNav",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_sip = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Mf_sip",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_expense_ratio = loop.run_until_complete(
        client.fetch_amc_data(
            filename="Expenceratio",
            date="30092022",
            section="MFOther",
            sub="",
            token=accord_token,
        ),
    )

    data_scheme_isin_master = loop.run_until_complete(
        client.fetch_amc_data(
            filename="schemeisinmaster",
            date="30092022",
            section="MFMaster",
            sub="",
            token=accord_token,
        ),
    )

    data_dict = {}
    classcode_mst = {}
    risk_mst = {}
    scheme_aum = {}
    nav_return = {}
    exit_load = {}
    scheme_ratio = {}
    scheme_sip = {}
    expense_ratio = {}
    scheme_plan = {}
    scheme_isin = {}

    for items in data_scheme_classcode["Table"]:
        classcode_mst[items["classcode"]] = {
            "scheme_type": items["asset_type"],
            "scheme_category": items["sub_category"],
        }

    for items in data_scheme_aum["Table"]:
        scheme_aum[items["schemecode"]] = {
            "aum": items["aum"],
        }

    for items in data_scheme_plan["Table"]:
        scheme_plan[items["plan_code"]] = {
            "scheme_plan": items["plan"],
        }

    for items in data_scheme_risk_level["Table"]:
        risk_mst[items["schemecode"]] = {
            "risk_level": items["color"],
        }

    for items in data_scheme_nav_return["Table"]:
        nav_return[items["schemecode"]] = {
            "nav": items["c_nav"],
            "return_last_year": items["1yrret"],
            "cagr": items["1yrret"],
            "return_last3_year": items["3yearret"],
            "return_last5_year": items["5yearret"],
            "return_since_inception": items["incret"],
        }

    for items in data_scheme_exit_load["Table"]:
        exit_load[items["SCHEMECODE"]] = {
            "exit_load": items["EXITLOAD"],
        }

    for items in data_scheme_ratio["Table"]:
        scheme_ratio[items["schemecode"]] = {
            "standard_deviation": items["sd"],
            "sharpe_ratio": items["sharpe"],
            "sortino_ratio": items["sortino"],
            "alpha": items["alpha"],
            "beta": items["beta"],
        }

    for items in data_scheme_sip["Table"]:
        scheme_sip[items["schemecode"]] = {
            "min_investment_sip": items["sipmininvest"],
        }

    for items in data_scheme_expense_ratio["Table"]:
        expense_ratio[items["schemecode"]] = {
            "ter": items["expratio"],
        }

    for items in data_scheme_isin_master["Table"]:
        scheme_isin[items["Schemecode"]] = {
            "isin": items["ISIN"],
        }

    for items in data_scheme["Table"]:
        data_dict[items["schemecode"]] = {
            "name": items["s_name"] if items["s_name"] else "NA",
            "amc_code": items["amc_code"] if items["amc_code"] else "NA",
            "scheme_plan": scheme_plan[items["plan"]]["scheme_plan"]
            if items["plan"] in scheme_plan
            else "NA",
            "scheme_type": classcode_mst[items["classcode"]]["scheme_type"]
            if items["classcode"] in classcode_mst
            else "NA",
            "scheme_category": classcode_mst[items["classcode"]]["scheme_category"]
            if items["classcode"] in classcode_mst
            else "NA",
            "nav": nav_return[items["schemecode"]]["nav"]
            if items["schemecode"] in nav_return
            else "0",
            # "isin": scheme_isin[items["schemecode"]]["isin"]
            # if items["schemecode"] in scheme_isin
            # else "NA",
            "cagr": nav_return[items["schemecode"]]["cagr"]
            if items["schemecode"] in nav_return
            else "0",
            "risk_level": risk_mst[items["schemecode"]]["risk_level"]
            if items["schemecode"] in risk_mst
            else "NA",
            "aum": scheme_aum[items["schemecode"]]["aum"]
            if items["schemecode"] in scheme_aum
            else "0",
            "ter": expense_ratio[items["schemecode"]]["ter"]
            if items["schemecode"] in expense_ratio
            else "0",
            "min_investment_sip": scheme_sip[items["schemecode"]]["min_investment_sip"]
            if items["schemecode"] in scheme_sip
            else "0",
            "exit_load": exit_load[items["schemecode"]]["exit_load"]
            if items["schemecode"] in exit_load
            else "NA",
            "fund_manager": items["fund_mgr1"] if items["fund_mgr1"] else "NA",
            "return_since_inception": nav_return[items["schemecode"]][
                "return_since_inception"
            ]
            if items["schemecode"] in nav_return
            else "0",
            "return_last_year": nav_return[items["schemecode"]]["return_last_year"]
            if items["schemecode"] in nav_return
            else "0",
            "return_last3_year": nav_return[items["schemecode"]]["return_last3_year"]
            if items["schemecode"] in nav_return
            else "0",
            "return_last5_year": nav_return[items["schemecode"]]["return_last5_year"]
            if items["schemecode"] in nav_return
            else "0",
            "standard_deviation": scheme_ratio[items["schemecode"]][
                "standard_deviation"
            ]
            if items["schemecode"] in scheme_ratio
            else "0",
            "sharpe_ratio": scheme_ratio[items["schemecode"]]["sharpe_ratio"]
            if items["schemecode"] in scheme_ratio
            else "0",
            "sortino_ratio": scheme_ratio[items["schemecode"]]["sortino_ratio"]
            if items["schemecode"] in scheme_ratio
            else "0",
            "alpha": scheme_ratio[items["schemecode"]]["alpha"]
            if items["schemecode"] in scheme_ratio
            else "0",
            "beta": scheme_ratio[items["schemecode"]]["beta"]
            if items["schemecode"] in scheme_ratio
            else "0",
        }

    dbsession = get_db_session()
    loop.run_until_complete(parse_and_save_scheme_data(data_dict, dbsession))
    logging.info("Fetched and saved AMC scheme data to the database.")


@celery.task(name="insert_dummy_data_to_db")
def save_dummy_data_to_db() -> None:
    """Insert dummy data to the database."""
    dbsession = get_db_session()
    loop = (
        asyncio.get_event_loop()
        if asyncio.get_event_loop()
        else asyncio.new_event_loop()
    )
    asyncio.set_event_loop(loop)
    loop.run_until_complete(insert_dummy_data(dbsession))
    logging.info("Inserted dummy data to the database.")


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
        name="Schedule task every 5 mins",
    )

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        dummy_scheduled_task.s("Happy Mondays!"),
        name="Schedule task every Monday at 7:30am",
    )

    # Calls fetch_amc_data_task() every day at 6 AM.
    sender.add_periodic_task(
        crontab(hour=6, minute=0),
        fetch_amc_data_task.s(),
        name="Fetch AMC data every day at 6 AM",
    )

    # Calls save_dummy_data_to_db() every 5 minute
    sender.add_periodic_task(
        5 * 60,
        save_dummy_data_to_db.s(),
        name="Insert dummy data to db",
    )

    # Calls fetch_amc_scheme_data_task() every day at 7 AM.
    sender.add_periodic_task(
        crontab(hour=7, minute=0),
        fetch_amc_scheme_data_task.s(),
        name="Fetch AMC scheme data every day at 7 AM",
    )
