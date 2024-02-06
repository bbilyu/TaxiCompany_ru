import datetime
from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, func, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base, StatusMixin, TableNameMixin


class Weekend(Base):
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
    __tablename__ = "Weekends"
    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    driver_id: Mapped[int]= mapped_column(Integer,ForeignKey('Drivers.driver_id'))
    week_day: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return f"<Weekend {self.Weekend} {self.driver_id} {self.week_day}>"
