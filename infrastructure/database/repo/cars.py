from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import Taxi_company
from infrastructure.database.models.cars import Car
from infrastructure.database.repo.base import BaseRepo


class CarRepo(BaseRepo):
    async def get_create_update_car(
            self,
            brand: str = None,
            model: str = None,
            release_year: int = None,
            state_number: str = None,
            cost: float = None,
            car_id: int = None,
            photo: str = None
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """
        if car_id:
            update_values = {}
            if brand:
                update_values['brand'] = brand
            if model:
                update_values['model'] = model
            if release_year:
                update_values['release_year'] = release_year
            if state_number:
                update_values['state_number'] = state_number
            if photo:
                update_values['photo'] = photo
            if cost:
                update_values['cost'] = cost

            update_stmt = (
                update(Car)
                .where(Car.car_id==car_id)
                .values(update_values)
                .returning(Car)
            )
            result = await self.session.execute(update_stmt)
        else:
            insert_stmt = (
                insert(Car)
                .values(
                    brand=brand,
                    model=model,
                    release_year=release_year,
                    state_number=state_number,
                    photo=photo,
                    cost=cost,
                )
                .returning(Car)
            )
            result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()


    async def get_car(self,car_id):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Car).filter(Car.car_id == car_id)
        result = await self.session.execute(q)
        return result.scalar_one()
    async def get_all_cars(
        self
    ):
        """
        Retrieves all cars from the database.
        :return: List of Car objects.
        """
        q = select(Car)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def get_all_active_cars_for_taxi_company(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Car).filter(Car.status == 1,Car.car_id.notin_(select(Taxi_company.car_id)))
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_all_active_cars(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Car).filter(Car.status == 1)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def get_all_not_active_cars(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """

        cars = await self.session.query(Car).filter(Car.status == 0).all()
        return cars

    async def delete_car(
            self, car_id: int
    ):
        """
        Deletes a car from the database by its id.
        :param car_id: The id of the car to delete
        :return: None
        """
        update_stmt = (
            update(Car)
            .where(Car.car_id==car_id)
            .values({"status":0})
            .returning(Car)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.scalar_one()