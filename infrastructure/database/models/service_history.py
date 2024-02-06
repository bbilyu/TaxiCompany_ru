import datetime
from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, func, ForeignKey, Float
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column


from .base import Base, StatusMixin, TableNameMixin


class Service_history(Base,StatusMixin):
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
    __tablename__ = "Service_history"
    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    car_id: Mapped[int]= mapped_column(Integer,nullable=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP)
    service_type: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)
    driver_id: Mapped[int]= mapped_column(Integer,nullable=True)
    performer_id: Mapped[int] = mapped_column(Integer, ForeignKey('Performers.performer_id'))

    # car = relationship("Car")
    # performer = relationship("Performer")

    def __repr__(self):
        return f"<Service_history {self.record_id} {self.service_type} {self.amount}>"
