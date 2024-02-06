import datetime
from typing import Union
from datetime import date
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import Taxi_company
from infrastructure.database.models.drivers import Driver
from infrastructure.database.repo.base import BaseRepo


class DriverRepo(BaseRepo):

    async def get_create_update_driver(
            self,
            surname: str = None,
            name: str = None,
            patronymic: str = None,
            birthdate: datetime = None,
            date_of_start_work: datetime = None,
            contact_information: str = None,
            additional_information: str = None,
            driver_id: int = None,
            date_of_termination: datetime = None,
            photo: str = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """
        if driver_id:
            update_values = {}
            if surname:
                update_values['surname'] = surname
            if name:
                update_values['name'] = name
            if patronymic:
                update_values['patronymic'] = patronymic
            if birthdate:
                update_values['birthdate'] = birthdate
            if date_of_start_work:
                update_values['date_of_start_work'] = date_of_start_work
            if contact_information:
                update_values['contact_information'] = contact_information
            if additional_information:
                update_values['additional_information'] = additional_information
            if photo:
                update_values['photo'] = photo
            update_stmt = (
                update(Driver)
                .where(Driver.driver_id==driver_id)
                .values(update_values)
                .returning(Driver)
            )
            result = await self.session.execute(update_stmt)
        else:
            insert_stmt = (
                insert(Driver)
                .values(
                    surname=surname,
                    name=name,
                    patronymic=patronymic,
                    birthdate=birthdate,
                    date_of_start_work=date_of_start_work,
                    contact_information=contact_information,
                    additional_information=additional_information,
                    photo=photo,
                )
                .returning(Driver)
            )
            result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_driver(self,driver_id):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Driver).filter(Driver.driver_id == driver_id)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_all_drivers(
        self
    ):
        """
        Retrieves all cars from the database.
        :return: List of Car objects.
        """
        q = select(Driver)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def get_all_active_drivers_for_taxi_company(self):
        """
       Retrieves all cars from the database where status = 1.
       :return: List of Car objects.
       """
        q = select(Driver).filter(Driver.status == 1,Driver.driver_id.notin_(select(Taxi_company.driver_id)))
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_all_active_drivers(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Driver).filter(Driver.status == 1)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_all_not_active_drivers(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """

        drivers = await self.session.query(Driver).filter(Driver.status == 0).all()
        return drivers

    async def delete_driver(
            self, driver_id: int
    ):
        """
        Deletes a car from the database by its id.
        :param driver_id: The id of the car to delete
        :return: None
        """
        update_stmt = (
            update(Driver)
            .where(Driver.driver_id==driver_id)
            .values({"status": 0,"date_of_termination": date.today()})
            .returning(Driver)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.scalar_one()