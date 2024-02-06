import asyncio
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.cars import CarRepo
from infrastructure.database.repo.compensation_for_damages import CompensationForDamageRepo
from infrastructure.database.repo.drivers import DriverRepo
from infrastructure.database.repo.other_expenses import OtherExpensesRepo
from infrastructure.database.repo.performers import PerformerRepo
from infrastructure.database.repo.recovery_from_damage import RecoveryFromDamageRepo
from infrastructure.database.repo.rent_payment import RentPaymentRepo
from infrastructure.database.repo.service_history import ServiceHistoryRepo
from infrastructure.database.repo.taxi_company import TaxiCompanyRepo
from infrastructure.database.repo.users import UserRepo
from infrastructure.database.repo.weekends import WeekendRepo
from infrastructure.database.setup import create_engine


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)

    @property
    def cars(self) -> CarRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return CarRepo(self.session)

    @property
    def drivers(self) -> DriverRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return DriverRepo(self.session)

    @property
    def compensation_for_damages(self) -> CompensationForDamageRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return CompensationForDamageRepo(self.session)

    @property
    def service_history(self) -> ServiceHistoryRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return ServiceHistoryRepo(self.session)

    @property
    def recovery_from_damages(self) -> RecoveryFromDamageRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return RecoveryFromDamageRepo(self.session)

    @property
    def other_expenses(self) -> OtherExpensesRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return OtherExpensesRepo(self.session)

    @property
    def performers(self) -> PerformerRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return PerformerRepo(self.session)

    @property
    def rent_payment(self) -> RentPaymentRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return RentPaymentRepo(self.session)


    @property
    def taxi_company(self) -> TaxiCompanyRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return TaxiCompanyRepo(self.session)

    @property
    def weekends(self) -> WeekendRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return WeekendRepo(self.session)


if __name__ == "__main__":
    from infrastructure.database.setup import create_session_pool
    from tgbot.config import Config, load_config


    async def example_usage(config: Config):
        """
        Example usage function for the RequestsRepo class.
        Use this function as a guide to understand how to utilize RequestsRepo for managing user data.
        Pass the config object to this function for initializing the database resources.
        :param config: The config object loaded from your configuration.
        """

        engine = create_engine(config.db)
        session_pool = create_session_pool(engine)

        async with session_pool() as session:
            repo = RequestsRepo(session)
            # date_string = "2024-01-08"
            # date_format = "%Y-%m-%d"
            # date = datetime.strptime(date_string, date_format)
            # rec  = await repo.compensation_for_damages.get_total_sum_with_date_where_car_id(car_id=1,user_date=date)
            # rec  = await repo.rent_payment.get_record_where_date_and_driver_id(driver_id=1,udate=date)
            # rec  = await repo.taxi_company.get_taxi_company_where_car_id(car_id=1)
            print(await repo.rent_payment.get_active_records_by_range("2018-02-13 00:00:00","2024-01-18 00:00:00",1))
            # print( await repo.cars.get_all_active_cars_for_taxi_company())
            # print(await repo.rent_payment.get_first_driver_payment(driver_id=1))
            # print(await repo.rent_payment.get_active_records_by_week(1))
            # print(await repo.other_expenses.get_create_update_other_expenses(1))
            # user = await repo.users.get_or_create_user(
            #     523993923,
            #     'Илья',
            #     'ru',
            #     'keepcalmaboss'
            # )
            # cars = await repo.cars.get_all_active_cars()
            # try:
            # print(await repo.taxi_company.get_driver_id_where_car_id(car_id=8))
            # await repo.compensation_for_damages.get_create_update_compensation_for_damages(car_id=1,
            #     driver_id=0,
            #     date=datetime.strptime("2022-01-19 00:00:00", "%Y-%m-%d %H:%M:%S"),
            #     description='fdsghdfgh',
            #     amount=123424,
            #     payers_id=3,
            # )
            # except:
            #     print("asfasf")
            # await repo.compensation_for_damages.get_create_update_compensation_for_damages(car_id=8,
            #     driver_id=4,
            #     date=datetime.strptime('2022-01-24 00:00:00', "%Y-%m-%d %H:%M:%S"),
            #     description='sdfgdfh',
            #     amount=23423423.0,
            #     payers_id=5,
            # )
            # await repo.cars.get_create_update_car(car_id=7,
            #     brand="avasfvasddv",
            # )
            # cars = await repo.cars.get_all_active_cars()
            # print(cars)
            # car = await repo.cars.get_or_create_car(brand="safg",
            #                                         model="sdghshhsd",
            #                                         release_year=2017,
            #                                         state_number="AAAAA",
            #                                         cost=5,
            #
            # )
            #
            # driver = await repo.drivers.get_or_create_driver(
            #     driver_id=1,
            #     surname = "gdrgerdg",
            #     name="fsdgsdg",
            #     patronymic="gsdgsdg",
            #     birthdate=datetime(2007, 12, 15),
            #     date_of_start_work=datetime(2022, 12, 15),
            #     contact_information="gsdfghdfhdfh",
            #     additional_information="gsdfghdfhdfh",
            # )
    asyncio.run(example_usage(config = load_config(".env")))