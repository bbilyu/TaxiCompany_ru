from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ListCallbackData(CallbackData, prefix="list"):
    record_id: int
    menu: str
class AddCallbackData(CallbackData, prefix="add"):
    add_menu: str

class CarCallbackData(CallbackData, prefix="car"):
    menu: str
class DriverCallbackData(CallbackData, prefix="driver"):
    menu: str

class ServiceHistoryCallbackData(CallbackData, prefix="service_history"):
    action: str
class CompensationForDamagesCallbackData(CallbackData, prefix="compensation_for_damages"):
    action: str
class RecoveryFromDamagesCallbackData(CallbackData, prefix="recovery_for_damages"):
    action: str
class OtherExpensesCallbackData(CallbackData, prefix="other_expenses"):
    action: str

class RentPaymentCallbackData(CallbackData, prefix="rent_payment"):
    action: str
class RentPaymentInManagementCallbackData(CallbackData, prefix="rent_payment_in_management"):
    id: int

class UpdateCarCallbackData(CallbackData, prefix="update_car"):
    change_menu: str
class UpdateDriverCallbackData(CallbackData, prefix="update_driver"):
    change_menu: str
class UpdateRentPaymentCallbackData(CallbackData, prefix="update_rent_payment"):
    action: str

class UpdateServiceHistoryCallbackData(CallbackData, prefix="update_service_history"):
    action: str
class UpdateCompensationForDamagesCallbackData(CallbackData, prefix="update_compensation_for_damages"):
    action: str
class UpdateRecoveryFromDamagesCallbackData(CallbackData, prefix="update_recovery_for_damages"):
    action: str
class UpdateOtherExpensesCallbackData(CallbackData, prefix="update_other_expenses"):
    action: str

class PerformerCallbackData(CallbackData, prefix="performer"):
    action: str
class MainCallbackData(CallbackData, prefix="main"):
    main_menu: str
class TaxiCompanyCallbackData(CallbackData, prefix="taxi_company"):
    taxi_company_menu: str
class ManagementCallbackData(CallbackData, prefix="management"):
    driver_id: int
    management_menu: str
class DriverInManagementCallbackData(CallbackData, prefix="driver_in_management"):
    driver_in_management_menu: str
class MediaCallbackData(CallbackData, prefix="media"):
    action: str
    menu: str
class DriverMediaCallbackData(CallbackData, prefix="drivermedia"):
    action: str
class WeekendsCallbackData(CallbackData, prefix="weekends"):
    weekday: int
    condition: str


class ConfirmationCallbackData(CallbackData, prefix="confirmation"):
    action: str
    answer: str
class ProfitRangeCallbackData(CallbackData, prefix="profit_range"):
    action: str
class RangeCallbackData(CallbackData, prefix="range"):
    action: str
    menu: str

class RemoveMediaCallbackData(CallbackData, prefix="remove_media"):
    menu: str
    record_id: int
class ChangeMediaCallbackData(CallbackData, prefix="change_media"):
    menu: str
class BackCallbackData(CallbackData, prefix="back"):
    back_menu: str
class SendMediaCallbackData(CallbackData, prefix="sendmedia"):
    key: str | int
class DateCallbackData(CallbackData, prefix="date"):
    date_type: str


def list_keyboard(record_id,menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"{record_id}",callback_data=ListCallbackData(record_id=record_id,menu=menu),
    )
    return keyboard.as_markup()
def last_list_keyboard(back_menu,text =None,add_menu = None):
    keyboard = InlineKeyboardBuilder()
    if text:
        keyboard.button(
            text=text, callback_data=AddCallbackData(add_menu=add_menu),
        )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=back_menu),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def change_media_keyboard(menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="Изменить", callback_data=ChangeMediaCallbackData(menu=menu,),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def remove_media_keyboard(menu,record_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="Удалить", callback_data=RemoveMediaCallbackData(menu=menu,record_id=record_id),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def car_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='📷 Осмотры 📷',callback_data=CarCallbackData(menu="inspections"),
    )
    keyboard.button(
        text="➕ Возмещение ущерба ➕", callback_data=CarCallbackData(menu="compensation_for_damages"),
    )
    keyboard.button(
        text="➖ Обслуживание ➖", callback_data=CarCallbackData(menu="service_history"),
    )
    keyboard.button(
        text="➖ Восстановление после ущерба ➖", callback_data=CarCallbackData(menu="recovery_from_damages"),
    )
    keyboard.button(
        text="➖ Прочие расходы ➖", callback_data=CarCallbackData(menu="other_expenses",),
    )
    keyboard.button(
        text="💰 Доходность 💰", callback_data=CarCallbackData(menu="profitability"),
    )
    keyboard.button(
        text="⚙️ Изменить ⚙️", callback_data=CarCallbackData(menu="change"),
    )
    keyboard.button(
        text="❌ Удалить ❌", callback_data=CarCallbackData(menu="remove"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="car_list"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def driver_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='📷 Медиа 📷',callback_data=DriverCallbackData(menu="media"),
    )
    keyboard.button(
        text="💳 Переводы 💳", callback_data=DriverCallbackData(menu="translations"),
    )
    keyboard.button(
        text="⚙️ Изменить ⚙️", callback_data=DriverCallbackData(menu="change"),
    )
    keyboard.button(
        text="❌ Уволить ❌", callback_data=DriverCallbackData(menu="dismiss"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="driver_list"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def performer_keyboard(menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='Выбрать',callback_data=PerformerCallbackData(action="choose"),
    )
    keyboard.button(
        text="Удалить", callback_data=PerformerCallbackData(action="remove"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=menu),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def service_history_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='📷 Медиа 📷',callback_data=ServiceHistoryCallbackData(action="media"),
    )
    keyboard.button(
        text="⚙️ Изменить ⚙️", callback_data=ServiceHistoryCallbackData(action="change"),
    )
    keyboard.button(
        text="❌ Удалить ❌", callback_data=ServiceHistoryCallbackData(action="remove"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="service_history"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def compensation_for_damages_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='📷 Медиа 📷', callback_data=CompensationForDamagesCallbackData(action="media"),
    )
    keyboard.button(
        text='⚙️ Изменить ⚙',callback_data=CompensationForDamagesCallbackData(action="change"),
    )
    keyboard.button(
        text="❌ Удалить ❌", callback_data=CompensationForDamagesCallbackData(action="remove"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="compensation_for_damages"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def recovery_from_damages_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='📷 Медиа 📷', callback_data=RecoveryFromDamagesCallbackData(action="media"),
    )
    keyboard.button(
        text='⚙️ Изменить ⚙',callback_data=RecoveryFromDamagesCallbackData(action="change"),
    )
    keyboard.button(
        text="❌ Удалить ❌", callback_data=RecoveryFromDamagesCallbackData(action="remove"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="recovery_from_damages"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def other_expenses_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='📷 Медиа 📷', callback_data=OtherExpensesCallbackData(action="media"),
    )
    keyboard.button(
        text='⚙️ Изменить ⚙',callback_data=OtherExpensesCallbackData(action="change"),
    )
    keyboard.button(
        text="❌ Удалить ❌", callback_data=OtherExpensesCallbackData(action="remove"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="other_expenses"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def rent_payment_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='⚙️ Изменить ⚙',callback_data=RentPaymentCallbackData(action="change"),
    )
    keyboard.button(
        text="❌ Удалить ❌", callback_data=RentPaymentCallbackData(action="remove"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="rent_payment"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def update_car_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Лицевое фото', callback_data=UpdateCarCallbackData(change_menu="facial_photo"),
    )
    keyboard.button(
        text='Марку',callback_data=UpdateCarCallbackData(change_menu="brand"),
    )
    keyboard.button(
        text="Модель", callback_data=UpdateCarCallbackData(change_menu="model"),
    )
    keyboard.button(
        text="Год выпуска", callback_data=UpdateCarCallbackData(change_menu="release_year"),
    )
    keyboard.button(
        text="Гос. номер", callback_data=UpdateCarCallbackData(change_menu="state_number"),
    )
    keyboard.button(
        text="Стоимость", callback_data=UpdateCarCallbackData(change_menu="cost"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="car_menu"),
    )
    keyboard.adjust(1)

    return keyboard.as_markup()
def update_driver_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Лицевое фото', callback_data=UpdateDriverCallbackData(change_menu="facial_photo"),
    )
    keyboard.button(
        text='Фамилию',callback_data=UpdateDriverCallbackData(change_menu="surname"),
    )
    keyboard.button(
        text="Имя", callback_data=UpdateDriverCallbackData(change_menu="name"),
    )
    keyboard.button(
        text="Отчество", callback_data=UpdateDriverCallbackData(change_menu="patronymic"),
    )
    keyboard.button(
        text="Дату рождения", callback_data=UpdateDriverCallbackData(change_menu="birthdate"),
    )
    keyboard.button(
        text="Дату начала работы", callback_data=UpdateDriverCallbackData(change_menu="start_work_date"),
    )
    keyboard.button(
        text="Контактную информацию", callback_data=UpdateDriverCallbackData(change_menu="contact_information"),
    )
    keyboard.button(
        text="Дополнительную информацию", callback_data=UpdateDriverCallbackData(change_menu="additional_information"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="driver_menu"),
    )
    keyboard.adjust(1)

    return keyboard.as_markup()
def update_rent_payment_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='Дату оплаты',callback_data=UpdateRentPaymentCallbackData(action="date_of_payment"),
    )
    keyboard.button(
        text="Комментарий", callback_data=UpdateRentPaymentCallbackData(action="comment"),
    )
    keyboard.button(
        text="Сумма", callback_data=UpdateRentPaymentCallbackData(action="amount"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="update_rent_payment"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def update_service_history_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='Дату обслуживания',callback_data=UpdateServiceHistoryCallbackData(action="date"),
    )
    keyboard.button(
        text="Тип обслуживания", callback_data=UpdateServiceHistoryCallbackData(action="service_type"),
    )
    keyboard.button(
        text="Cтоимость обслуживания", callback_data=UpdateServiceHistoryCallbackData(action="amount"),
    )
    keyboard.button(
        text="Исполнителя", callback_data=UpdateServiceHistoryCallbackData(action="performer"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="update_service_history"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def update_compensation_for_damages_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='Дату',callback_data=UpdateCompensationForDamagesCallbackData(action="date"),
    )
    keyboard.button(
        text="Описание", callback_data=UpdateCompensationForDamagesCallbackData(action="description"),
    )
    keyboard.button(
        text="Стоимость возмещения", callback_data=UpdateCompensationForDamagesCallbackData(action="amount"),
    )
    keyboard.button(
        text="Плательщика", callback_data=UpdateCompensationForDamagesCallbackData(action="payers"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="update_compensation_for_damages"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def update_recovery_from_damages_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='Дату',callback_data=UpdateRecoveryFromDamagesCallbackData(action="date"),
    )
    keyboard.button(
        text="Описание", callback_data=UpdateRecoveryFromDamagesCallbackData(action="description"),
    )
    keyboard.button(
        text="Стоимость восстановления", callback_data=UpdateRecoveryFromDamagesCallbackData(action="amount"),
    )
    keyboard.button(
        text="Плательщика", callback_data=UpdateRecoveryFromDamagesCallbackData(action="payers"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="update_recovery_from_damages"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def update_other_expenses_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='Дату',callback_data=UpdateOtherExpensesCallbackData(action="date"),
    )
    keyboard.button(
        text="Описание", callback_data=UpdateOtherExpensesCallbackData(action="description"),
    )
    keyboard.button(
        text="Стоимость расхдов", callback_data=UpdateOtherExpensesCallbackData(action="amount"),
    )
    keyboard.button(
        text="Исполнителя", callback_data=UpdateOtherExpensesCallbackData(action="performer"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu="update_other_expenses"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def back_keyboard(menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=menu),
    )

    return keyboard.as_markup()
def send_media_keyboard(key):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="Отправить файлы", callback_data=SendMediaCallbackData(key=key),
    )

    return keyboard.as_markup()
def date_keyboard(menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="СЕГОДНЯ", callback_data=DateCallbackData(date_type="today"),
    )
    keyboard.button(
        text="КАЛЕНДАРЬ", callback_data=DateCallbackData(date_type="calendar"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=menu),
    )

    return keyboard.as_markup()

def main_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="АВТОМОБИЛИ 🚕", callback_data=MainCallbackData(main_menu="cars"),
    )
    keyboard.button(
        text="ВОДИТЕЛИ 🙍‍♂", callback_data=MainCallbackData(main_menu="drivers"),
    )
    keyboard.button(
        text="ТАКСОПАРК 🚖", callback_data=MainCallbackData(main_menu="taxi_company"),
    )
    return keyboard.as_markup()
def taxi_company_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="УПРАВЛЕНИЕ 🚕 - 👨", callback_data=TaxiCompanyCallbackData(taxi_company_menu="management"),
    )
    keyboard.button(
        text="ДОХОДНОСТЬ 💰", callback_data=TaxiCompanyCallbackData(taxi_company_menu="profitability"),
    )
    keyboard.button(
        text="ПЕРЕВОДЫ 💳", callback_data=TaxiCompanyCallbackData(taxi_company_menu="translations"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu='main'),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def driver_in_management_keyboard(key):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Арендную плату", callback_data=DriverInManagementCallbackData(driver_in_management_menu="rent_payment"),
    )
    keyboard.button(
        text="График выходных", callback_data=DriverInManagementCallbackData(driver_in_management_menu="weekends"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=key),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def weekends_keyboard(weekends,key):
    weekdays_name_full = {1: "Понедельник",
                          2: "Вторник",
                          3: "Среда",
                          4: "Четверг",
                          5: "Пятница",
                          6: "Суббота",
                          7: "Воскресенье"}
    for weekend in weekends:
        weekdays_name_full[weekend] += " ✅"
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=weekdays_name_full[1],callback_data=WeekendsCallbackData(weekday=1,condition="on" if 1 in weekends else "off"))
    keyboard.button(text=weekdays_name_full[2],callback_data = WeekendsCallbackData(weekday=2,condition="on" if 2 in weekends else "off"))
    keyboard.button(text=weekdays_name_full[3],callback_data = WeekendsCallbackData(weekday=3,condition="on" if 3 in weekends else "off"))
    keyboard.button(text=weekdays_name_full[4],callback_data = WeekendsCallbackData(weekday=4,condition="on" if 4 in weekends else "off"))
    keyboard.button(text=weekdays_name_full[5],callback_data = WeekendsCallbackData(weekday=5,condition="on" if 5 in weekends else "off"))
    keyboard.button(text=weekdays_name_full[6],callback_data = WeekendsCallbackData(weekday=6,condition="on" if 6 in weekends else "off"))
    keyboard.button(text=weekdays_name_full[7],callback_data = WeekendsCallbackData(weekday=7,condition="on" if 7 in weekends else "off"))
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=key),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def management_keyboard(driver_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Водитель", callback_data=ManagementCallbackData(management_menu="driver",driver_id=driver_id),
    )
    keyboard.button(
        text="Удалить связку", callback_data=ManagementCallbackData(management_menu="remove",driver_id=driver_id),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def carmedia_keyboard(back_menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="ПОВРЕЖДЕНИЯ", callback_data=MediaCallbackData(action="damage",menu="car"),
    )
    keyboard.button(
        text="ОСМОТРЫ", callback_data=MediaCallbackData(action="inspections",menu="car"),
    )
    keyboard.button(
        text="ЛИЦЕВОЕ ФОТО", callback_data=MediaCallbackData(action="facial_photo",menu="car"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=back_menu),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def drivermedia_keyboard(back_menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="ДОКУМЕНТЫ", callback_data=MediaCallbackData(action="documents",menu="driver"),
    )
    keyboard.button(
        text="ЛИЦЕВОЕ ФОТО", callback_data=MediaCallbackData(action="facial_photo",menu="driver"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=back_menu),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def profit_range_keyboard(menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='год',callback_data=ProfitRangeCallbackData(action="year"),
    )
    keyboard.button(
        text="весь диапазон", callback_data=ProfitRangeCallbackData(action="all_time"),
    )
    keyboard.button(
        text="выбранный диапазон", callback_data=ProfitRangeCallbackData(action="range"),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=menu),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def range_keyboard(menu,back_menu):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text='неделю',callback_data=RangeCallbackData(action="week",menu=menu),
    )
    keyboard.button(
        text="месяц", callback_data=RangeCallbackData(action="month",menu=menu),
    )
    keyboard.button(
        text="весь диапазон", callback_data=RangeCallbackData(action="all_time",menu=menu),
    )
    keyboard.button(
        text="выбранный диапазон", callback_data=RangeCallbackData(action="range",menu=menu),
    )
    keyboard.button(
        text="◀ назад", callback_data=BackCallbackData(back_menu=back_menu),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def confirmation_keyboard(action):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="Да", callback_data=ConfirmationCallbackData(action=action,answer="yes"),
    )
    keyboard.button(
        text="Нет", callback_data=ConfirmationCallbackData(action=action,answer="no"),
    )
    return keyboard.as_markup()








# For a more advanced usage of callback_data, you can use the CallbackData factory
class OrderCallbackData(CallbackData, prefix="order"):
    """
    This class represents a CallbackData object for orders.

    - When used in InlineKeyboardMarkup, you have to create an instance of this class, run .pack() method, and pass to callback_data parameter.

    - When used in InlineKeyboardBuilder, you have to create an instance of this class and pass to callback_data parameter (without .pack() method).

    - In handlers you have to import this class and use it as a filter for callback query handlers, and then unpack callback_data parameter to get the data.

    # Example usage in simple_menu.py
    """
    order_id: int


def my_orders_keyboard(orders: list):
    # Here we use a list of orders as a parameter (from simple_menu.py)

    keyboard = InlineKeyboardBuilder()
    for order in orders:
        keyboard.button(
            text=f"📝 {order['title']}",
            # Here we use an instance of OrderCallbackData class as callback_data parameter
            # order id is the field in OrderCallbackData class, that we defined above
            callback_data=OrderCallbackData(order_id=order["id"])
        )

    return keyboard.as_markup()


class TypesOfProvisionCD(CallbackData, prefix="type_of_provision"):
    type: Optional[str]
    increase: Optional[bool]
    finish: Optional[bool]
    reset: Optional[bool]


class RequestCD(CallbackData, prefix="request"):
    active: bool
    request_id: int


def get_types_of_provision_keyboard(provision_types: dict):
    builder = InlineKeyboardBuilder()

    for provision_type, quantity in provision_types.items():
        builder.add(
            InlineKeyboardButton(
                text=f'{provision_type} ({quantity})',
                callback_data=TypesOfProvisionCD(type=provision_type).pack(),
            ),

            InlineKeyboardButton(
                text="+",
                callback_data=TypesOfProvisionCD(type=provision_type, increase=True).pack(),
            ),
        )

    builder.add(
        InlineKeyboardButton(text='Отправить ✔', callback_data=TypesOfProvisionCD(finish=True).pack())
    )
    builder.add(
        InlineKeyboardButton(text='Сброс ❌', callback_data=TypesOfProvisionCD(reset=True).pack())
    )
    builder.adjust(
        *[2] * len(provision_types),  # [name, +]
        1, 2  # [finish]
    )

    return builder.as_markup()


def approve_request_keyboard(current_request_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=RequestCD(active=True, request_id=current_request_id).pack()),
            InlineKeyboardButton(text="Нет",
                                 callback_data=RequestCD(active=False, request_id=current_request_id).pack()),
        ]
    ])
    return keyboard