from typing import Generic, Mapping, Optional, Sequence, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from myfi_backend.db.models.base_model import BaseModel

T = TypeVar("T", bound=BaseModel)  # noqa: WPS111


class BaseDAO(Generic[T]):
    """Base class for models."""

    __abstract__ = True

    def __init__(self, model: Type[T], session: AsyncSession):
        """
        Initialize the BaseDAO with a model and session.

        :param model: The model class to operate on.
        :param session: The database session.
        """
        self.model = model
        self.session = session

    async def get_all(self) -> Sequence[T]:
        """
        Get all instances of the model.

        :return: List of all model instances.
        """
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, instance_id: UUID) -> Optional[T]:
        """
        Get a model instance by id.

        :param instance_id: The id of the model instance to get.
        :return: The model instance if found, else None.
        """
        stmt = select(self.model).where(self.model.id == instance_id)
        result = await self.session.execute(stmt)
        instance = result.scalars().first()
        return instance if instance else None

    async def create(self, kwargs: Mapping[str, Union[str, UUID]]) -> T:
        """
        Create a new model instance.

        :param kwargs: The attributes of the model instance.
        :return: The created model instance.
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: T) -> T:
        """
        Update an existing model instance.

        :param instance: The model instance to update.
        :return: The updated model instance.
        """
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance_id: UUID) -> Optional[T]:
        """
        Delete a model instance by id.

        :param instance_id: The id of the model instance to delete.
        :return: The deleted model instance.
        """
        instance: Optional[T] = await self.get_by_id(instance_id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
        return instance
