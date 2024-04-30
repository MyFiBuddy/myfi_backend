from typing import Mapping, Optional, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme


class MutualFundSchemeDAO(BaseDAO[MutualFundScheme]):
    """
    Data Access Object for MutualFundScheme model.

    Provides interface for CRUD operations on MutualFundScheme model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(MutualFundScheme, session)

    async def get_by_code(self, scheme_code: int) -> Optional[MutualFundScheme]:
        """
        Get a model instance by amc code.

        :param scheme_code: The code of the scheme instance to get.
        :return: The scheme instance if found, else None.
        """
        result = await self.session.execute(
            select(MutualFundScheme).filter_by(scheme_id=scheme_code),
        )
        instance = result.scalars().first()
        return instance if instance else None

    async def upsert(
        self,
        scheme_data: Mapping[str, Union[str, UUID, float, int]],
    ) -> MutualFundScheme:
        """
        Perform an upsert operation on AMC.

        If an scheme with the provided code exists, update it. Otherwise,
        create a new scheme.

        :param scheme_data: Dictionary containing AMC scheme data.
        :return: The updated or created AMC scheme.
        """
        result = await self.session.execute(
            select(MutualFundScheme).filter_by(name=scheme_data["name"]),
        )
        scheme = result.scalars().first()

        if scheme is None:
            # AMC scheme with this code does not exist, create a new one
            scheme = MutualFundScheme(**scheme_data)
            self.session.add(scheme)
        else:
            # AMC scheme with this code exists, update it
            for key, value in scheme_data.items():
                setattr(scheme, key, value)
        return scheme
