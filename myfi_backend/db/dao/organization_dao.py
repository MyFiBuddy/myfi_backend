from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.organization_model import Organization


class OrganizationDAO(BaseDAO[Organization]):
    """
    Data Access Object for Organization model.

    Provides interface for CRUD operations on Organization model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)
