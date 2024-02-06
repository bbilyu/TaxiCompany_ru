import datetime
from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, func, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column


from .base import Base, StatusMixin


class Driver(Base, StatusMixin):
    """
    This class represents a User in the application.
    If you want to learn more about SQLAlchemy and Alembic, you can check out the following link to my course:
    https://www.udemy.com/course/sqlalchemy-alembic-bootcamp/?referralCode=E9099C5B5109EB747126

    Attributes:
        user_id (Mapped[int]): The unique identifier of the user.
        username (Mapped[Optional[str]]): The username of the user.
        full_name (Mapped[str]): The full name of the user.
        active (Mapped[bool]): Indicates whether the user is active or not.
        language (Mapped[str]): The language preference of the user.

    Methods:
        __repr__(): Returns a string representation of the User object.

    Inherited Attributes:
        Inherits from Base, TimestampMixin, and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin, and TableNameMixin classes, which provide additional functionality.

    """
    __tablename__ = "Drivers"

    driver_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    surname: Mapped[str]= mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(128))
    patronymic: Mapped[str] = mapped_column(String(128))
    birthdate: Mapped[datetime] = mapped_column(TIMESTAMP)
    date_of_start_work: Mapped[datetime] = mapped_column(TIMESTAMP)
    date_of_termination: Mapped[datetime] = mapped_column(TIMESTAMP,default=None, nullable=True)
    contact_information: Mapped[str] = mapped_column(String(100))
    additional_information: Mapped[str] = mapped_column(String(255))
    photo: Mapped[str] = mapped_column(String(255),server_default=None, nullable=True)

    taxi_company = relationship("Taxi_company", back_populates="driver", overlaps="taxi_company")

    def __repr__(self):
        return f"<Driver {self.driver_id} {self.surname} {self.name} {self.patronymic}>"
