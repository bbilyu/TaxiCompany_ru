from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, text, Float
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from .base import Base, StatusMixin


class Car(Base, StatusMixin):
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
    __tablename__ = "Cars"
    car_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str]= mapped_column(String(128))
    model: Mapped[str] = mapped_column(String(128))
    release_year: Mapped[int] = mapped_column(Integer)
    state_number: Mapped[str] = mapped_column(String(15),unique=True)
    photo: Mapped[str] = mapped_column(String(255),default=None, nullable=True)
    cost: Mapped[float] = mapped_column(Float)

    taxi_company = relationship("Taxi_company", back_populates="car", overlaps="taxi_company")


    def __repr__(self):
        return f"<Car {self.car_id} {self.brand} {self.model} {self.state_number}>"
