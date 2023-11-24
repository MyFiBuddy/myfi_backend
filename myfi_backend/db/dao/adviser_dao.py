from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.adviser_model import Adviser


class AdviserDAO(BaseDAO[Adviser]):
    """
    Data Access Object for Adviser model.

    Provides interface for CRUD operations on Adviser model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Adviser, session)

    async def get_by_external_id(self, external_id: str) -> Optional[Adviser]:
        """
        Get an Adviser instance by external_id.

        :param external_id: The external_id of the Adviser instance to get.
        :return: The Adviser instance if found, else None.
        """
        stmt = select(self.model).where(self.model.external_id == external_id)
        result = await self.session.execute(stmt)
        instance = result.scalars().first()
        return instance if instance else None
