# employee_dao.py
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.employee_model import Employee


class EmployeeDAO(BaseDAO[Employee]):
    """
    Data Access Object for Employee model.

    Provides interface for CRUD operations on Employee model.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Employee, session)

    async def get_by_external_id(self, external_id: str) -> Optional[Employee]:
        """
        Get an Employee instance by external_id.

        :param external_id: The external_id of the Employee instance to get.
        :return: The Employee instance if found, else None.
        """
        stmt = select(self.model).where(self.model.external_id == external_id)
        result = await self.session.execute(stmt)
        instance = result.scalars().first()
        return instance if instance else None
