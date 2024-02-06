import datetime

from sqlalchemy import delete, select, update, func, extract
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models.other_expenses import Other_expenses
from infrastructure.database.repo.base import BaseRepo


class OtherExpensesRepo(BaseRepo):
    async def get_create_update_other_expenses(
            self,
            record_id: int = None,
            car_id: int = None,
            date: datetime = None,
            description: str = None,
            amount: float = None,
            driver_id: int = None,
            performer_id: int = None,
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
            if date:
                update_values['date'] = date
            if description:
                update_values['description'] = description
            if amount:
                update_values['amount'] = amount
            if driver_id:
                update_values['driver_id'] = driver_id
            if performer_id:
                update_values['performer_id'] = performer_id

            update_stmt = (
                update(Other_expenses)
                .where(Other_expenses.record_id==record_id)
                .values(update_values)
                .returning(Other_expenses)
            )
            result = await self.session.execute(update_stmt)
        else:
            insert_stmt = (
                insert(Other_expenses)
                .values(
                    car_id=car_id,
                    date=date,
                    description=description,
                    amount=amount,
                    driver_id=driver_id,
                    performer_id=performer_id,
                )
                .returning(Other_expenses)
            )
            result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_total_sum(self):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.sum(Other_expenses.amount)).filter(Other_expenses.status==1)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_total_sum_with_date(self, user_date):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.sum(Other_expenses.amount)).filter(Other_expenses.status==1,
                                                 extract('month', Other_expenses.date)==user_date.month,
                                                 extract('year', Other_expenses.date)==user_date.year)
        result = await self.session.execute(q)
        return result.scalar_one()


    async def get_total_sum_where_car_id(self, car_id):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.sum(Other_expenses.amount)).filter(Other_expenses.car_id==car_id,
                                                 Other_expenses.status==1)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_total_sum_with_date_where_car_id(self, car_id, user_date):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.sum(Other_expenses.amount)).filter(Other_expenses.car_id==car_id,
                                                 Other_expenses.status==1,
                                                 extract('month', Other_expenses.date)==user_date.month,
                                                 extract('year', Other_expenses.date)==user_date.year)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_all_other_expenses(
        self
    ):
        """
        Retrieves all cars from the database.
        :return: List of Car objects.
        """
        q = select(Other_expenses)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_all_active_other_expenses_where_id(self, car_id):
        """
        Retrieves all compensations for damages from the database for a specific car_id with status = 1.
        :param car_id: ID of the car.
        :return: List of Compensation_for_damage objects.
        """

        q = select(Other_expenses).filter(Other_expenses.status==1, Other_expenses.car_id==car_id)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def get_all_active_other_expenses(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """
        q = select(Other_expenses).filter(Other_expenses.status == 1)
        result = await self.session.execute(q)
        return result.scalars().all()
    async def get_all_not_active_other_expenses(self):
        """
        Retrieves all cars from the database where status = 1.
        :return: List of Car objects.
        """

        cars = await self.session.query(Other_expenses).filter(Other_expenses.status == 0).all()
        return cars

    async def remove_other_expenses(
            self, record_id: int
    ):
        """
        Deletes a car from the database by its id.
        :param car_id: The id of the car to delete
        :return: None
        """

        update_stmt = (
            update(Other_expenses)
            .where(Other_expenses.record_id==record_id)
            .values({"status": 0})
            .returning(Other_expenses)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.scalar_one()
