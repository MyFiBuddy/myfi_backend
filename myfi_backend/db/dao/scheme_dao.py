from typing import Mapping, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.amc_scheme_model import SCHEME


class SchemeDAO(BaseDAO[SCHEME]):
    """
    Data Access Object for AMC model.

    Provides interface for CRUD operations on AMC model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(SCHEME, session)

    async def upsert(
        self,
        amc_data: Mapping[str, Union[str, UUID, float]],
    ) -> SCHEME:
        """
        Perform an upsert operation on AMC Scheme.

        If an AMC Scheme with the provided code exists, update it. Otherwise,
        create a new AMC Scheme.

        :param amc_data: Dictionary containing AMC Scheme data.
        :return: The updated or created AMC Scheme.
        """
        result = await self.session.execute(
            select(SCHEME).filter_by(code=amc_data["code"]),
        )
        scheme = result.scalars().first()
        if scheme is None:
            # AMC with this code does not exist, create a new one
            scheme = SCHEME(**amc_data)
            self.session.add(scheme)
        else:
            # AMC with this code exists, update it
            for key, value in amc_data.items():
                setattr(scheme, key, value)
        return scheme
