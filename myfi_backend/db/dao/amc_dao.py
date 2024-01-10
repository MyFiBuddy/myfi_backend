from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.amc_model import AMC


class AmcDAO(BaseDAO[AMC]):
    """
    Data Access Object for AMC model.

    Provides interface for CRUD operations on AMC model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(AMC, session)
