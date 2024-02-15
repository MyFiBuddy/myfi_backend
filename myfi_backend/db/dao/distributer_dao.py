from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.distributor_model import Distributor


class DistributorDAO(BaseDAO[Distributor]):
    """
    Data Access Object for Distributor model.

    Provides interface for CRUD operations on Distributor model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Distributor, session)

    async def get_by_external_id(self, external_id: str) -> Optional[Distributor]:
        """
        Get an Distributor instance by external_id.

        :param external_id: The external_id of the Distributor instance to get.
        :return: The Distributor instance if found, else None.
        """
        stmt = select(self.model).where(self.model.external_id == external_id)
        result = await self.session.execute(stmt)
        instance = result.scalars().first()
        return instance if instance else None
