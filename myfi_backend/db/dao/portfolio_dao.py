from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.models.portfolio_model import Portfolio, PortfolioMutualFund


class PortfolioDAO(BaseDAO[Portfolio]):
    """Data Access Object for Portfolio model. Extends BaseDAO."""

    def __init__(self, session: AsyncSession):
        super().__init__(Portfolio, session)

    async def get_by_id(self, instance_id: UUID) -> Optional[Portfolio]:
        """
        Get a model instance by id.

        :param instance_id: The id of the model instance to get.
        :return: The model instance if found, else None.
        """
        stmt = (
            select(Portfolio)
            .options(
                joinedload(Portfolio.mutual_fund_schemes),
                joinedload(Portfolio.adviser),
            )
            .where(Portfolio.id == instance_id)
        )
        result = await self.session.execute(stmt)
        instance = result.scalars().first()
        return instance if instance else None


class PortfolioMutualFundDAO(BaseDAO[PortfolioMutualFund]):
    """Data Access Object for PortfolioMutualFund model. Extends BaseDAO."""

    def __init__(self, session: AsyncSession):
        super().__init__(PortfolioMutualFund, session)

    async def get_by_id(self, instance_id: UUID) -> Optional[PortfolioMutualFund]:
        """
        Get a model instance by id.

        :param instance_id: The id of the model instance to get.
        :return: The model instance if found, else None.
        """
        stmt = (
            select(PortfolioMutualFund)
            .options(
                joinedload(PortfolioMutualFund.portfolio),
                joinedload(PortfolioMutualFund.mutualfundscheme),
            )
            .where(PortfolioMutualFund.id == instance_id)
        )
        result = await self.session.execute(stmt)
        instance = result.scalars().first()
        return instance if instance else None

    async def update_schemes_in_portfolio(
        self,
        portfolio_id: UUID,
        schemes_with_proportions: List[Tuple[int, int]],
    ) -> None:
        """
        Update the schemes of a portfolio.

        This method deletes all existing schemes from the portfolio and adds the new
        schemes with their proportions.

        :param portfolio_id: The ID of the portfolio to update.
        :param schemes_with_proportions: A list of tuples, where each tuple contains a
            scheme ID and a proportion.
        :raises ValueError: If proportions do not sum to 100.
        """
        # Check that the sum of the proportions is 100
        if sum(proportion for _, proportion in schemes_with_proportions) != 100:
            raise ValueError(
                "The sum of the proportions of all schemes in the portfolio must be"
                "100.",
            )

        # Delete all existing schemes from the portfolio
        stmt = delete(PortfolioMutualFund).where(
            PortfolioMutualFund.portfolio_id == portfolio_id,
        )
        await self.session.execute(stmt)

        # Add the new schemes to the portfolio
        for scheme_id, proportion in schemes_with_proportions:
            await self.create(
                {
                    "portfolio_id": portfolio_id,
                    "mutualfundscheme_id": scheme_id,
                    "proportion": proportion,
                },
            )

        await self.session.commit()
