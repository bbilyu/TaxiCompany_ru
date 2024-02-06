import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models.weekends import Weekend
from infrastructure.database.repo.base import BaseRepo


class WeekendRepo(BaseRepo):
    async def get_create_update_weekend(
            self,
            record_id: int = None,
            driver_id: int = None,
            week_day: int = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """
        if record_id:
            update_values = {}
            if driver_id:
                update_values['driver_id'] = driver_id
            if week_day:
                update_values['week_day'] = week_day

            update_stmt = (
                update(Weekend)
                .where(Weekend.record_id==record_id)
                .values(update_values)
                .returning(Weekend)
            )
            result = await self.session.execute(update_stmt)
        else:
            insert_stmt = (
                insert(Weekend)
                .values(
                    driver_id=driver_id,
                    week_day=week_day,
                )
                .returning(Weekend)
            )
            result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_all_weekends_where_driver_id(
        self,
            driver_id: int
    ):
        """
        Retrieves all cars from the database.
        :return: List of Car objects.
        """
        q = select(Weekend.week_day).filter_by(driver_id=driver_id)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def delete_weekend(
            self, driver_id: int,week_day:int
    ):
        """
        Deletes a car from the database by its id.
        :param car_id: The id of the car to delete
        :return: None
        """

        q = delete(Weekend).where(Weekend.driver_id == driver_id,Weekend.week_day == week_day)
        await self.session.execute(q)
        await self.session.commit()