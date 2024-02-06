import datetime

from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models.performers import Performer
from infrastructure.database.repo.base import BaseRepo


class PerformerRepo(BaseRepo):

    async def get_create_update_performer(
            self,
            performer_id: int = None,
            performer_name: str = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """
        if performer_id:
            update_values = {}
            if performer_name:
                update_values['performer_name'] = performer_name
            update_stmt = (
                update(Performer)
                .where(Performer.performer_id==performer_id)
                .values(update_values)
                .returning(Performer)
            )
            result = await self.session.execute(update_stmt)
        else:
            insert_stmt = (
                insert(Performer)
                .values(
                    performer_name=performer_name,
                )
                .returning(Performer)
            )
            result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_performer(self,performer_id):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Performer).filter(Performer.performer_id == performer_id)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_all_performers(
        self
    ):
        """
        Retrieves all cars from the database.
        :return: List of Car objects.
        """
        q = select(Performer)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_all_active_performers(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Performer).filter(Performer.status == 1)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def get_all_not_active_performers(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """

        cars = await self.session.query(Performer).filter(Performer.status == 0).all()
        return cars

    async def remove_performer(
            self, performer_id: int
    ):
        """
        Deletes a car from the database by its id.
        :param car_id: The id of the car to delete
        :return: None
        """
        update_stmt = (
            update(Performer)
            .where(Performer.performer_id==performer_id)
            .values({"status": 0})
            .returning(Performer)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.scalar_one()