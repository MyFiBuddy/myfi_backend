import logging
from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from myfi_backend.celery.tasks import dummy_task
from myfi_backend.db.dao.dummy_dao import DummyDAO
from myfi_backend.db.models.dummy_model import Dummy
from myfi_backend.web.api.dummy.schema import DummyDTO, DummyInputDTO

router = APIRouter()


@router.get("/", response_model=List[DummyDTO])
async def get_dummy_models(
    limit: int = 10,
    offset: int = 0,
    dummy_dao: DummyDAO = Depends(),
) -> List[Dummy]:
    """
    Retrieve all dummy objects from the database.

    :param limit: limit of dummy objects, defaults to 10.
    :param offset: offset of dummy objects, defaults to 0.
    :param dummy_dao: DAO for dummy models.
    :return: list of dummy objects from database.
    """
    logging.info("Sending dummy task to celery")
    dummy_task.delay()
    return await dummy_dao.get_all_dummies(limit=limit, offset=offset)


@router.put("/")
async def create_dummy_model(
    new_dummy_object: DummyInputDTO,
    dummy_dao: DummyDAO = Depends(),
) -> None:
    """
    Creates dummy model in the database.

    :param new_dummy_object: new dummy model item.
    :param dummy_dao: DAO for dummy models.
    """
    await dummy_dao.create_dummy_model(**new_dummy_object.dict())
