from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.mutual_fund_scheme_model import MutualFundScheme


class MutualFundSchemeDAO(BaseDAO[MutualFundScheme]):
    """
    Data Access Object for MutualFundScheme model.

    Provides interface for CRUD operations on MutualFundScheme model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(MutualFundScheme, session)
