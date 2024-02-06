import datetime

from sqlalchemy import update, select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from infrastructure.database.models.taxi_company import Taxi_company
from infrastructure.database.repo.base import BaseRepo


class TaxiCompanyRepo(BaseRepo):

    async def get_create_update_taxi_company(
            self,
            record_id: str = None,
            car_id: str = None,
            driver_id: int = None,
            driver_rent: float = None,
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
            if car_id:
                update_values['car_id'] = car_id
            if driver_id:
                update_values['driver_id'] = driver_id
            if driver_rent:
                update_values['driver_rent'] = driver_rent

            update_stmt = (
                update(Taxi_company)
                .where(Taxi_company.record_id==record_id)
                .values(update_values)
                .returning(Taxi_company)
            )
            result = await self.session.execute(update_stmt)
        else:
            insert_stmt = (
                insert(Taxi_company)
                .values(
                    car_id=car_id,
                    driver_id=driver_id,
                    driver_rent=driver_rent,
                )
                .returning(Taxi_company)
            )
            result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()
    async def get_taxi_company_where_car_id(self, car_id):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """

        q = select(Taxi_company).filter(Taxi_company.car_id==car_id)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def get_driver_id_where_car_id(self, car_id):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """

        q = select(Taxi_company).filter(Taxi_company.car_id==car_id)
        result = await self.session.execute(q)
        return result.scalar_one().driver_id
    async def get_car_id_where_driver_id(self, driver_id):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """

        q = select(Taxi_company).filter(Taxi_company.driver_id==driver_id)
        result = await self.session.execute(q)
        return result.scalar_one().car_id
    async def get_object_where_driver_id(self, driver_id):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """

        q = select(Taxi_company).options(selectinload(Taxi_company.car)).filter(Taxi_company.driver_id==driver_id)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_driver_rent_where_driver_id(self, driver_id):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """

        q = select(Taxi_company).filter(Taxi_company.driver_id==driver_id)
        result = await self.session.execute(q)
        return result.scalar_one().driver_rent
    async def get_driver_rent_where_driver_id(self, driver_id):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """

        q = select(Taxi_company).filter(Taxi_company.driver_id==driver_id)
        result = await self.session.execute(q)
        return result.scalar_one().driver_rent
    async def set_driver_rent_where_driver_id(self, driver_id,driver_rent):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """
        update_stmt = (
            update(Taxi_company)
            .where(Taxi_company.driver_id==driver_id)
            .values({"driver_rent":driver_rent})
            .returning(Taxi_company)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.scalar_one()
    async def get_all_taxi_company(
        self
    ):
        """
        Retrieves all cars from the database.
        :return: List of Car objects.
        """
        q = select(Taxi_company)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def remove_taxi_company(
            self, driver_id: int= None,car_id:int = None
    ):
        """
        Deletes a car from the database by its id.
        :param car_id: The id of the car to delete
        :return: None
        """
        if driver_id:
            q = delete(Taxi_company).where(Taxi_company.driver_id == driver_id)
        elif car_id:
            q = delete(Taxi_company).where(Taxi_company.car_id==car_id)
        await self.session.execute(q)
        await self.session.commit()
