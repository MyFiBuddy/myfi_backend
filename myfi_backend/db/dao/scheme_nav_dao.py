import logging
from typing import Dict, Mapping, Optional, Union
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.attributes import flag_modified

from myfi_backend.db.dao.base_dao import BaseDAO
from myfi_backend.db.dependencies import get_db_session
from myfi_backend.db.models.scheme_nav_model import SchemeNAV


class SchemeNavDAO(BaseDAO[SchemeNAV]):
    """
    Data Access Object for SchemeNAV model.

    Provides interface for CRUD operations on SchemeNAV model.
    """

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(SchemeNAV, session)

    async def create(
        self,
        kwargs: Mapping[str, Union[str, UUID, float, Dict[str, float]]],
    ) -> SchemeNAV:
        """
        Create a new model instance.

        :param kwargs: The attributes of the model instance.
        :return: The created model instance.
        :raises ValueError: If 'nav_data' is not present in kwargs
                            or it's not a dictionary.
        """
        mutable_kwargs = dict(kwargs)
        if "nav_data" not in mutable_kwargs or not isinstance(
            mutable_kwargs["nav_data"],
            dict,
        ):
            raise ValueError("nav_data not present or nav_data must be a dictionary")

        mutable_kwargs["nav_data"] = dict(sorted(mutable_kwargs["nav_data"].items()))

        instance = self.model(**mutable_kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: SchemeNAV) -> SchemeNAV:
        """
        Update an existing model instance.

        :param instance: The model instance to update.
        :return: The updated model instance.
        """
        if instance.nav_data and isinstance(instance.nav_data, dict):
            sorted_nav_data = dict(sorted(instance.nav_data.items()))
            instance.nav_data = sorted_nav_data

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_scheme_id(self, scheme_id: UUID) -> Optional[SchemeNAV]:
        """
        Get a model instance by scheme id.

        :param scheme_id: The id of the scheme instance to get.
        :return: The SchemeNAV instance if found, else None.
        """
        result = await self.session.execute(
            select(SchemeNAV).filter_by(scheme_id=scheme_id),
        )
        instance = result.scalars().first()
        return instance if instance else None

    async def upsert(
        self,
        scheme_nav_data: Mapping[str, Union[UUID, Dict[str, float]]],
    ) -> Optional[SchemeNAV]:
        """
        Perform an upsert operation on SchemeNAV.

        If a SchemeNAV with the provided scheme_id exists, update its nav_data.
        Otherwise, create a new SchemeNAV.

        :param scheme_nav_data: Dictionary representing the SchemeNAV model.
        :return: The updated or created SchemeNAV.
        """
        scheme_id = scheme_nav_data["scheme_id"]
        nav_data = scheme_nav_data["nav_data"]

        result = await self.session.execute(
            select(SchemeNAV).filter_by(scheme_id=scheme_id),
        )
        scheme_nav = result.scalars().first()

        if isinstance(nav_data, dict):
            sorted_nav_data = dict(sorted(nav_data.items()))
        else:
            logging.error(
                f"nav_data is not a dictionary for scheme_id: {scheme_id}, "
                f"didn't upsert NAV data",
            )
            return None

        if scheme_nav is None:
            # SchemeNAV with this scheme_id does not exist, create a new one
            scheme_nav = SchemeNAV(scheme_id=scheme_id, nav_data=sorted_nav_data)
            self.session.add(scheme_nav)
        elif isinstance(scheme_nav.nav_data, dict):
            # SchemeNAV with this scheme_id exists, update its nav_data
            scheme_nav.nav_data.update(sorted_nav_data)
            # Inform SQLAlchemy that nav_data has been updated
            flag_modified(scheme_nav, "nav_data")
        else:
            logging.error(
                f"nav_data is not a dictionary for scheme_id: {scheme_id}, "
                f"didn't upsert NAV data",
            )
        return scheme_nav

    async def add_latest_nav(
        self,
        scheme_id: UUID,
        date: str,
        nav: float,
    ) -> Optional[SchemeNAV]:
        """
        Add the latest NAV to the nav_data of a SchemeNAV.

        If a SchemeNAV with the provided scheme_id exists, add the latest NAV to its
        nav_data. Otherwise, create a new SchemeNAV.

        :param scheme_id: The id of the scheme.
        :param date: The date of the latest NAV.
        :param nav: The latest NAV.
        :return: The updated or created SchemeNAV.
        """
        result = await self.session.execute(
            select(SchemeNAV).filter_by(scheme_id=scheme_id),
        )
        scheme_nav = result.scalars().first()

        if scheme_nav is None:
            # SchemeNAV with this scheme_id does not exist, create a new one
            scheme_nav = SchemeNAV(scheme_id=scheme_id, nav_data={date: nav})
            self.session.add(scheme_nav)
        elif isinstance(scheme_nav.nav_data, dict):
            # SchemeNAV with this scheme_id exists, add the latest NAV to its nav_data
            scheme_nav.nav_data[date] = nav
            scheme_nav.nav_data = dict(sorted(scheme_nav.nav_data.items()))
            flag_modified(scheme_nav, "nav_data")
        else:
            logging.error(
                f"nav_data is not a dictionary for scheme_id: {scheme_id}, didn't add "
                f"latest NAV",
            )
            return None

        await self.session.commit()
        await self.session.refresh(scheme_nav)
        return scheme_nav
