from datetime import datetime, date, timedelta

from sqlalchemy import update, func, select, extract, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from infrastructure.database.models.rent_payment import Rent_payment
from infrastructure.database.repo.base import BaseRepo


class RentPaymentRepo(BaseRepo):
    async def get_create_update_rent_payment(
            self,
            payment_id: int = None,
            car_id: int = None,
            driver_id: int = None,
            date: datetime = None,
            comment: str = None,
            amount: float = None,
            driver_rent: int = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """
        if payment_id:
            update_values = {}
            if car_id:
                update_values['car_id'] = car_id
            if driver_id:
                update_values['driver_id'] = driver_id
            if date:
                update_values['date'] = date
            if comment:
                update_values['comment'] = comment
            if amount:
                update_values['amount'] = amount
            if driver_rent:
                update_values['driver_rent'] = driver_rent

            update_stmt = (
                update(Rent_payment)
                .where(Rent_payment.payment_id==payment_id)
                .values(update_values)
                .returning(Rent_payment)
            )
            result = await self.session.execute(update_stmt)
        else:
            insert_stmt = (
                insert(Rent_payment)
                .values(
                    car_id=car_id,
                    driver_id=driver_id,
                    date=date,
                    comment=comment,
                    amount=amount,
                    driver_rent=driver_rent,
                )
                .returning(Rent_payment)
            )
            result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()


    async def get_record_where_date_and_driver_id(self, driver_id, udate):
        """
        Retrieves rent payment records for a specific driver and date.
        :param driver_id: The driver ID.
        :param udate: The date to search for.
        :return: List of rent payment records for the driver and date.
        """

        q = select(Rent_payment).options(selectinload(Rent_payment.car)).filter(Rent_payment.driver_id==driver_id, Rent_payment.date==udate)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_first_date_where_car_id(self,car_id):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.min(Rent_payment.date)).filter(Rent_payment.car_id==car_id)
        result = await self.session.execute(q)
        return result.scalar_one().date()
    async def get_latest_date_where_car_id(self,car_id):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.max(Rent_payment.date)).filter(Rent_payment.car_id==car_id)
        result = await self.session.execute(q)
        return result.scalar_one().date()
    async def get_first_date(self):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = func.min(Rent_payment.date)
        result = await self.session.execute(q)
        return result.scalar_one()
    async def get_latest_date(self):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = func.max(Rent_payment.date)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_total_sum(self):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.sum(Rent_payment.amount)).filter(Rent_payment.status==1)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_total_sum_with_date(self, user_date):
        """
        Retrieves rent payment records within a specific month and year.
        :param user_date: The date to filter the records.
        :return: The total sum of rent payment records within the specified date.
        """

        q = select(func.sum(Rent_payment.amount)).filter(
            Rent_payment.status==1,
            extract('month', Rent_payment.date)==user_date.month,
            extract('year', Rent_payment.date)==user_date.year
        )
        result = await self.session.execute(q)
        return result.scalar_one()


    async def get_total_sum_where_car_id(self,car_id):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.sum(Rent_payment.amount)).filter(Rent_payment.car_id==car_id,
            Rent_payment.status==1)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_total_sum_with_date_where_car_id(self,car_id,user_date):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(func.sum(Rent_payment.amount)).filter(Rent_payment.car_id==car_id,
            Rent_payment.status==1,
            extract('month', Rent_payment.date) == user_date.month,
            extract('year', Rent_payment.date) == user_date.year)
        result = await self.session.execute(q)
        return result.scalar_one()

    async def get_all_active_records(self,driver_id):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(Rent_payment).filter(Rent_payment.status==1,Rent_payment.driver_id==driver_id)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_first_driver_payment(self,driver_id):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        q = select(Rent_payment).filter(Rent_payment.driver_id==driver_id).order_by(Rent_payment.date.desc())
        result = await self.session.execute(q)
        return result.scalars().first()
    async def get_active_records_by_week(self,driver_id):
        """
        Retrieves rent payment records within a specific week.
        :param start_date: The start date of the week.
        :param end_date: The end date of the week.
        :return: List of rent payment records within the specified week.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        q = select(Rent_payment).filter(Rent_payment.status==1,Rent_payment.driver_id==driver_id,Rent_payment.date.between(start_date, end_date))
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_active_records_by_month(self,driver_id):
        """
        Retrieves rent payment records within a specific month.
        :param year: The year of the month.
        :param month: The month.
        :return: List of rent payment records within the specified month.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        q = select(Rent_payment).filter(Rent_payment.status==1,Rent_payment.driver_id==driver_id,Rent_payment.date.between(start_date, end_date))
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_active_records_by_range(self, start_date: str, end_date: str,driver_id):
        """
        Retrieves rent payment records within a specified date range.
        :param start_date: The start date of the range.
        :param end_date: The end date of the range.
        :return: List of rent payment records within the specified date range.
        """
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        q = select(Rent_payment).filter(Rent_payment.status==1,Rent_payment.driver_id==driver_id,Rent_payment.date.between(start_date, end_date))
        result = await self.session.execute(q)
        return result.scalars().all()
    async def remove_rent_payment(
            self, payment_id: int
    ):
        """
        Deletes a car from the database by its id.
        :param car_id: The id of the car to delete
        :return: None
        """

        update_stmt = (
            update(Rent_payment)
            .where(Rent_payment.payment_id==payment_id)
            .values({"status": 0})
            .returning(Rent_payment)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.scalar_one()