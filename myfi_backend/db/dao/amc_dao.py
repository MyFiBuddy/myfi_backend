from typing import Mapping, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.amc_model import AMC


class AmcDAO(BaseDAO[AMC]):
    """
    Data Access Object for AMC model.

    Provides interface for CRUD operations on AMC model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(AMC, session)

    async def upsert(self, amc_data: Mapping[str, Union[str, UUID, float]]) -> AMC:
        """
        Perform an upsert operation on AMC.

        If an AMC with the provided code exists, update it. Otherwise, create a new AMC.

        :param amc_data: Dictionary containing AMC data.
        :return: The updated or created AMC.
        """
        result = await self.session.execute(
            select(AMC).filter_by(code=amc_data["code"]),
        )
        amc = result.scalars().first()

        if amc is None:
            # AMC with this code does not exist, create a new one
            amc = AMC(**amc_data)
            self.session.add(amc)
        else:
            # AMC with this code exists, update it
            for key, value in amc_data.items():
                setattr(amc, key, value)
        return amc
