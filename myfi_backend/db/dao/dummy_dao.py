from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.dependencies import get_db_session
from myfi_backend.db.models.dummy_model import Dummy


class DummyDAO(BaseDAO[Dummy]):
    """Class for accessing dummy table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_dummy_model(self, name: str) -> None:
        """
        Add single dummy to session.

        :param name: name of a dummy.
        """
        self.session.add(Dummy(name=name))

    async def get_all_dummies(self, limit: int, offset: int) -> List[Dummy]:
        """
        Get all dummy models with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of dummies.
        """
        raw_dummies = await self.session.execute(
            select(Dummy).limit(limit).offset(offset),
        )

        return list(raw_dummies.scalars().fetchall())

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[Dummy]:
        """
        Get specific dummy model.

        :param name: name of dummy instance.
        :return: dummy models.
        """
        query = select(Dummy)
        if name:
            query = query.where(Dummy.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
