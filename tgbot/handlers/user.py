import asyncio
import os
from datetime import datetime, date, timedelta
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram_calendar import SimpleCalendarCallback, DialogCalendarCallback, SimpleCalendar, DialogCalendar

from tgbot.filters.private_chat import IsPrivate
from tgbot.filters.user import UserFilter
from tgbot.keyboards.inline import main_keyboard, MainCallbackData, last_list_keyboard, \
    AddCallbackData, back_keyboard, BackCallbackData, list_keyboard, ListCallbackData, car_keyboard, \
    driver_keyboard, CarCallbackData, DriverCallbackData, \
    confirmation_keyboard, ConfirmationCallbackData, update_car_keyboard, update_driver_keyboard, \
    performer_keyboard, PerformerCallbackData, range_keyboard, RangeCallbackData, \
    taxi_company_keyboard, management_keyboard, TaxiCompanyCallbackData, ManagementCallbackData, \
    driver_in_management_keyboard, DriverInManagementCallbackData, weekends_keyboard, WeekendsCallbackData, \
    compensation_for_damages_keyboard, service_history_keyboard, recovery_from_damages_keyboard, \
    other_expenses_keyboard, ServiceHistoryCallbackData, UpdateDriverCallbackData, UpdateCarCallbackData, \
    update_service_history_keyboard, CompensationForDamagesCallbackData, update_compensation_for_damages_keyboard, \
    RecoveryFromDamagesCallbackData, OtherExpensesCallbackData, update_recovery_from_damages_keyboard, \
    update_other_expenses_keyboard, UpdateServiceHistoryCallbackData, UpdateCompensationForDamagesCallbackData, \
    UpdateRecoveryFromDamagesCallbackData, UpdateOtherExpensesCallbackData, profit_range_keyboard, \
    ProfitRangeCallbackData, remove_media_keyboard, RemoveMediaCallbackData, \
    UpdateRentPaymentCallbackData, update_rent_payment_keyboard, rent_payment_keyboard, RentPaymentCallbackData
from tgbot.middlewares.album import AlmubMiddleware
from tgbot.middlewares.cleaner import DeleteMessagesMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.functions import convert_days_to_years_months_days, calculate_return_on_investment
from tgbot.misc.states import AddCar, AddDriver, UpdateCar, UpdateDriver, AddCompensationForDamages, AddPerformer, \
    AddServiceHistory, AddRecoveryFromDamages, AddOtherExpenses, AddRange, AddRentPayment, AddManagement, \
    UpdateDriverInManagement, UpdateServiceHistory, UpdateCompensationForDamages, UpdateRecoveryFromDamages, \
    UpdateOtherExpenses, AddProfitRange, AddMedia, UpdateRentPayment

user_router = Router()


logger = None

# Установка текущего логгера
def set_current_logger(log):
    global logger
    logger = log

middlewares = [ThrottlingMiddleware(1,0.5),DeleteMessagesMiddleware()]
user_router.message.middleware(AlmubMiddleware())
for middleware in middlewares:
    user_router.message.middleware(middleware)
    user_router.callback_query.middleware(middleware)

filters = [UserFilter()]
PHOTOS_DIR = 'media'

for filter in filters:
    user_router.message.filter(filter)
    user_router.callback_query.filter(filter)

month_names = {
        'January': 'января',
        'February': 'февраля',
        'March': 'марта',
        'April': 'апреля',
        'May': 'мая',
        'June': 'июня',
        'July': 'июля',
        'August': 'августа',
        'September': 'сентября',
        'October': 'октября',
        'November': 'ноября',
        'December': 'декабря'
    }
weekdays_name = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Вс"}
weekdays_name_full = {1: "Понедельник",
                      2: "Вторник",
                      3: "Среда",
                      4: "Четверг",
                      5: "Пятница",
                      6: "Суббота",
                      7: "Воскресенье"}
async def driver_list(update,bot_custom,repo,menu = "driver"):
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    match menu:
        case "management__driver":
            drivers = await repo.drivers.get_all_active_drivers_for_taxi_company()
        case _:
            drivers = await repo.drivers.get_all_active_drivers()
    for driver in drivers:
        birthday = driver.birthdate
        start_work_date = driver.date_of_start_work
        if driver.photo:
            photo_path = os.path.join(PHOTOS_DIR, "driver", str(driver.driver_id), "facial_photo", f"{driver.photo}.jpg")
            photo = FSInputFile(photo_path)
            bot_custom.messages[message.chat.id].append(await message.answer_photo(photo=photo, caption=f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}", reply_markup=list_keyboard(record_id=driver.driver_id,menu=menu)))
        else:
            bot_custom.messages[message.chat.id].append(await message.answer(f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}", reply_markup=list_keyboard(record_id=driver.driver_id,menu = menu)))

    match menu:
        case "driver":
            return bot_custom.messages[message.chat.id].append(await message.answer("ВОДИТЕЛИ 🙍‍♂", reply_markup=last_list_keyboard(add_menu=menu, back_menu="main", text="Добавить водителя")))
        case "compensation_for_damages__driver" | "management__driver":
            if drivers:
                return bot_custom.messages[message.chat.id].append(await message.answer("Выберите водителя", reply_markup=last_list_keyboard(back_menu="management")))
            else:
                return bot_custom.messages[message.chat.id].append(await message.answer("Водители отсутствуют!\nДобавьте водителя в меню 'ВОДИТЕЛИ 🙍‍♂'", reply_markup=last_list_keyboard(back_menu="management")))
async def car_list(update,bot_custom,repo,menu = "car"):
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    match menu:
        case "management":
            cars = await repo.cars.get_all_active_cars_for_taxi_company()
        case _:
            cars = await repo.cars.get_all_active_cars()
    for car in cars:
        if car.photo:
            photo_path = os.path.join(PHOTOS_DIR, "car", str(car.car_id), "facial_photo", f"{car.photo}.jpg")
            photo = FSInputFile(photo_path)
            bot_custom.messages[message.chat.id].append(await message.answer_photo(photo=photo, caption=f"Марка: {car.brand}\nМодель: {car.model}\nГод выпуска: {car.release_year}\nГос номер: {car.state_number}", reply_markup=list_keyboard(record_id=car.car_id,menu=menu)))
        else:
            bot_custom.messages[message.chat.id].append(await message.answer(f"Марка: {car.brand}\nМодель: {car.model}\nГод выпуска: {car.release_year}\nГос номер: {car.state_number}", reply_markup=list_keyboard(record_id=car.car_id,menu=menu)))
    match menu:
        case "car":
            return bot_custom.messages[message.chat.id].append(await message.answer("АВТОМОБИЛИ 🚕", reply_markup=last_list_keyboard(add_menu=menu, back_menu="main", text="Добавить авто")))
        case "management":
            if cars:
                return bot_custom.messages[message.chat.id].append(await message.answer("Выберите автомобиль", reply_markup=last_list_keyboard(back_menu="management")))
            else:
                return bot_custom.messages[message.chat.id].append(await message.answer("Автомобили отсутствуют!\nДобавьте автомобиль в меню 'АВТОМОБИЛИ 🚕'", reply_markup=last_list_keyboard(back_menu="management")))

        case "compensation_for_damages__car":
            if cars:
                return bot_custom.messages[message.chat.id].append(await message.answer("Выберите автомобиль", reply_markup=last_list_keyboard(back_menu="main")))
            else:
                return bot_custom.messages[message.chat.id].append(await message.answer("Автомобили отсутствуют!\nДобавьте автомобиль в меню 'АВТОМОБИЛИ 🚕'", reply_markup=last_list_keyboard(back_menu="main")))


async def inspections_list(update,state,bot_custom,repo):
    data = await state.get_data()
    car_id = data.get("car_id")
    match data.get("range"):
        case "week":
            start_date = date.today()
            user_date_start = start_date - timedelta(days=7)
            user_date_end = None
        case "month":
            start_date = date.today()
            user_date_start = start_date - timedelta(days=30)
            user_date_end = None
        case "all_time":
            user_date_start = None
            user_date_end = None
        case "user_range":
            user_date_start = datetime.strptime(data.get("start_date"), "%Y-%m-%d %H:%M:%S").date()
            user_date_end = datetime.strptime(data.get("end_date"), "%Y-%m-%d %H:%M:%S").date()
    menu = "inspections"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    media_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), menu)
    if os.path.isdir(media_dir):
        dates_dirs = sorted([d for d in os.listdir(media_dir) if os.path.isdir(os.path.join(media_dir, d))])
        for dates_dir in dates_dirs:
            date_dirr_date = datetime.strptime(dates_dir, '%d_%m_%Y').date()
            key = False
            if user_date_start:
                if user_date_end:
                    if date_dirr_date >= user_date_start and date_dirr_date <= user_date_end:
                        key = True
                else:
                    if date_dirr_date >= user_date_start:
                        key = True
            else:
                key = True
            if key:
                date_dir = os.path.join(media_dir, dates_dir)
                medias = sorted(os.listdir(date_dir))
                counter = 0
                media_path_out = {}
                for media in medias:
                    if "archive" not in media:
                        media_path = os.path.join(date_dir, media)
                        media_path_out.update({counter:media_path})
                        driver_id = int(media.split("_")[0])
                        if driver_id:
                            driver = await repo.drivers.get_driver(driver_id=driver_id)
                            driver = f"{driver.surname} {driver.name} {driver.patronymic}"
                        else:
                            driver = "отсутствует"
                        if media_path[-1]=="4":
                            video = FSInputFile(media_path)
                            date_dirr = datetime.strptime(dates_dir, '%d_%m_%Y')
                            date_dirr_str = date_dirr.strftime("%d %B %Y")
                            month = date_dirr.strftime('%B')
                            date_dirr = date_dirr_str.replace(month, month_names[month])
                            bot_custom.messages[message.chat.id].append(await message.answer_video(video=video, caption=f"Дата: {date_dirr}\nВодитель: {driver}", reply_markup=remove_media_keyboard(menu=menu,record_id=counter)))
                        else:
                            photo = FSInputFile(media_path)
                            date_dirr = datetime.strptime(dates_dir, '%d_%m_%Y')
                            date_dirr_str = date_dirr.strftime("%d %B %Y")
                            month = date_dirr.strftime('%B')
                            date_dirr = date_dirr_str.replace(month, month_names[month])
                            bot_custom.messages[message.chat.id].append(await message.answer_photo(photo=photo, caption=f"Дата: {date_dirr}\nВодитель: {driver}", reply_markup=remove_media_keyboard(menu=menu,record_id=counter)))
                        counter += 1
                await state.update_data(media_path=media_path_out)
    match menu:
        case "inspections":
            return bot_custom.messages[message.chat.id].append(await message.answer("📷 Осмотры 📷", reply_markup=last_list_keyboard(add_menu=menu, back_menu="car", text="Добавить осмотр")))
async def expenses_list(update,state,bot_custom,repo):
    data = await state.get_data()
    car_id = data.get("car_id")
    menu = data.get("menu")
    last_underscore_index = menu.rfind("_")  # Находим индекс последнего подчеркивания
    menu = menu[:last_underscore_index]  # Удаляем текст после последнего подчеркивания
    record_id = data.get(menu+"_id")
    match data.get("range"):
        case "week":
            start_date = date.today()
            user_date_start = start_date - timedelta(days=7)
            user_date_end = None
        case "month":
            start_date = date.today()
            user_date_start = start_date - timedelta(days=30)
            user_date_end = None
        case "all_time":
            user_date_start = None
            user_date_end = None
        case "user_range":
            user_date_start = datetime.strptime(data.get("start_date"), "%Y-%m-%d %H:%M:%S").date()
            user_date_end = datetime.strptime(data.get("end_date"), "%Y-%m-%d %H:%M:%S").date()
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    media_dir = os.path.join(PHOTOS_DIR, "car", str(car_id),menu,str(record_id))
    if os.path.isdir(media_dir):
        dates_dirs = sorted([d for d in os.listdir(media_dir) if os.path.isdir(os.path.join(media_dir, d))])
        for dates_dir in dates_dirs:
            date_dirr_date = datetime.strptime(dates_dir, '%d_%m_%Y').date()
            key = False
            if user_date_start:
                if user_date_end:
                    if date_dirr_date >= user_date_start and date_dirr_date <= user_date_end:
                        key = True
                else:
                    if date_dirr_date >= user_date_start:
                        key = True
            else:
                key = True
            if key:
                date_dir = os.path.join(media_dir, dates_dir)
                medias = sorted(os.listdir(date_dir))
                counter = 0
                media_path_out = {}
                for media in medias:
                    if "archive" not in media:
                        media_path = os.path.join(date_dir, media)
                        media_path_out.update({counter: media_path})

                        driver_id = int(media.split("_")[0])
                        if driver_id:
                            driver = await repo.drivers.get_driver(driver_id=driver_id)
                            driver = f"{driver.surname} {driver.name} {driver.patronymic}"
                        else:
                            driver = "отсутствует"
                        if media_path[-1]=="4":
                            video = FSInputFile(media_path)

                            date_dirr = datetime.strptime(dates_dir, '%d_%m_%Y')
                            date_dirr_str = date_dirr.strftime("%d %B %Y")
                            month = date_dirr.strftime('%B')
                            date_dirr = date_dirr_str.replace(month, month_names[month])

                            bot_custom.messages[message.chat.id].append(await message.answer_video(video=video, caption=f"Дата: {date_dirr}\nВодитель: {driver}", reply_markup=remove_media_keyboard(menu=menu,record_id=counter)))

                        else:
                            photo = FSInputFile(media_path)

                            date_dirr = datetime.strptime(dates_dir, '%d_%m_%Y')
                            date_dirr_str = date_dirr.strftime("%d %B %Y")
                            month = date_dirr.strftime('%B')
                            date_dirr = date_dirr_str.replace(month, month_names[month])

                            bot_custom.messages[message.chat.id].append(await message.answer_photo(photo=photo, caption=f"Дата: {date_dirr}\nВодитель: {driver}", reply_markup=remove_media_keyboard(menu=menu,record_id=counter)))
                        counter += 1
                await state.update_data(media_path=media_path_out)
    match menu:
        case "compensation_for_damages":
            text = "📷 Медиа возмещение ущерба 📷"
        case "service_history":
            text = "📷 Медиа обслуживания 📷"
        case "recovery_from_damages":
            text = "📷 Медиа восстановление после ущерба 📷"
        case "other_expenses":
            text = "📷 Медиа прочих расходов 📷"
    return bot_custom.messages[message.chat.id].append(await message.answer(text, reply_markup=last_list_keyboard(add_menu=menu + "_media", back_menu="update_" + menu, text="Добавить медиа")))

async def media_list(update,state,bot_custom,repo):
    data = await state.get_data()
    driver_id = data.get("driver_id")
    match data.get("range"):
        case "week":
            start_date = date.today()
            user_date_start = start_date - timedelta(days=7)
            user_date_end = None
        case "month":
            start_date = date.today()
            user_date_start = start_date - timedelta(days=30)
            user_date_end = None
        case "all_time":
            user_date_start = None
            user_date_end = None
        case "user_range":
            user_date_start = datetime.strptime(data.get("start_date"), "%Y-%m-%d %H:%M:%S").date()
            user_date_end = datetime.strptime(data.get("end_date"), "%Y-%m-%d %H:%M:%S").date()
    menu = "media"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    media_dir = os.path.join(PHOTOS_DIR, "driver", str(driver_id), menu)
    if os.path.isdir(media_dir):
        dates_dirs = sorted([d for d in os.listdir(media_dir) if os.path.isdir(os.path.join(media_dir, d))])
        for dates_dir in dates_dirs:
            date_dirr_date = datetime.strptime(dates_dir, '%d_%m_%Y').date()
            key = False
            if user_date_start:
                if user_date_end:
                    if date_dirr_date >= user_date_start and date_dirr_date <= user_date_end:
                        key = True
                else:
                    if date_dirr_date >= user_date_start:
                        key = True
            else:
                key = True
            if key:
                date_dir = os.path.join(media_dir, dates_dir)
                medias = sorted(os.listdir(date_dir))
                counter = 0
                media_path_out = {}
                for media in medias:
                    if "archive" not in media:
                        media_path = os.path.join(date_dir, media)
                        media_path_out.update({counter: media_path})
                        car_id = int(media.split("_")[0])
                        if car_id:
                            car = await repo.cars.get_car(car_id=car_id)
                            car = f"{car.brand} {car.model} {car.state_number}"
                        else:
                            car = "отсутствует"
                        if media_path[-1]=="4":
                            video = FSInputFile(media_path)
                            date_dirr = datetime.strptime(dates_dir, '%d_%m_%Y')
                            date_dirr_str = date_dirr.strftime("%d %B %Y")
                            month = date_dirr.strftime('%B')
                            date_dirr = date_dirr_str.replace(month, month_names[month])
                            bot_custom.messages[message.chat.id].append(await message.answer_video(video=video, caption=f"Дата: {date_dirr}\nАвтомобиль: {car}", reply_markup=remove_media_keyboard(menu=menu,record_id=counter)))

                        else:
                            photo = FSInputFile(media_path)
                            date_dirr = datetime.strptime(dates_dir, '%d_%m_%Y')
                            date_dirr_str = date_dirr.strftime("%d %B %Y")
                            month = date_dirr.strftime('%B')
                            date_dirr = date_dirr_str.replace(month, month_names[month])
                            bot_custom.messages[message.chat.id].append(await message.answer_photo(photo=photo, caption=f"Дата: {date_dirr}\nАвтомобиль: {car}", reply_markup=remove_media_keyboard(menu=menu,record_id=counter)))
                        counter += 1
                await state.update_data(media_path=media_path_out)
    match menu:
        case "media":
            return bot_custom.messages[message.chat.id].append(await message.answer("📷 Медиа 📷", reply_markup=last_list_keyboard(add_menu=menu, back_menu="driver", text="Добавить медиа")))
async def performer_list(update,bot_custom,repo,menu = "performer"):
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    performers = await repo.performers.get_all_active_performers()
    for performer in performers:
        bot_custom.messages[message.chat.id].append(await message.answer(performer.performer_name, reply_markup=list_keyboard(record_id=performer.performer_id,menu=menu)))
    match menu:
        case "service_history__performer"| "other_expenses__performer":
            return bot_custom.messages[message.chat.id].append(await message.answer("Исполнители 👷‍♂️", reply_markup=last_list_keyboard(add_menu=menu, back_menu="amount", text="Добавить исполнителя")))
        case "compensation_for_damages__performer" | "recovery_from_damages__performer":
            return bot_custom.messages[message.chat.id].append(await message.answer("Плательщики 👷‍♂️", reply_markup=last_list_keyboard(add_menu=menu, back_menu="amount", text="Добавить плательщика")))
        case "update_service_history__performer":
            return bot_custom.messages[message.chat.id].append(await message.answer("Исполнители 👷‍♂️", reply_markup=last_list_keyboard(add_menu=menu, back_menu="update_service_history__performer", text="Добавить исполнителя")))
        case "update_compensation_for_damages__performer":
            return bot_custom.messages[message.chat.id].append(await message.answer("Плательщики 👷‍♂️", reply_markup=last_list_keyboard(add_menu=menu, back_menu="update_compensation_for_damages__performer", text="Добавить плательщика")))
        case "update_recovery_from_damages__performer":
            return bot_custom.messages[message.chat.id].append(await message.answer("Плательщики 👷‍♂️", reply_markup=last_list_keyboard(add_menu=menu, back_menu="update_recovery_from_damages__performer", text="Добавить плательщика")))
        case "update_other_expenses__performer":
            return bot_custom.messages[message.chat.id].append(await message.answer("Исполнители 👷‍♂️", reply_markup=last_list_keyboard(add_menu=menu, back_menu="update_other_expenses__performer", text="Добавить исполнителя")))
        case "compensation_for_damages__car":
            return bot_custom.messages[message.chat.id].append(await message.answer("Выберите автомобиль", reply_markup=last_list_keyboard(back_menu="main")))

async def compensation_for_damages_list(update,state,bot_custom,repo):
    menu = "compensation_for_damages"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    data = await state.get_data()
    car_id = data.get("car_id")
    compensation_for_damages = await repo.compensation_for_damages.get_all_active_compensations_for_damages_where_id(car_id)
    for compensation in compensation_for_damages:
        performer = await repo.performers.get_performer(performer_id=compensation.payers_id)
        if compensation.driver_id == 0:
            driver = "не назначен"
        else:
            driver = await repo.drivers.get_driver(driver_id=compensation.driver_id)
            driver = f"{driver.surname} {driver.name} {driver.patronymic}"
        post_time = compensation.date
        post_time_str = post_time.strftime("%d %B %Y")
        month = post_time.strftime('%B')
        bot_custom.messages[message.chat.id].append(await message.answer(f"Дата : {post_time_str.replace(month,month_names[month])}\nОписание: {compensation.description}\nСумма: {compensation.amount}\nВодитель: {driver}\nПлательщик: {performer.performer_name}\n", reply_markup=list_keyboard(record_id=compensation.record_id,menu=menu)))
    return bot_custom.messages[message.chat.id].append(await message.answer("Возмещение ущерба", reply_markup=last_list_keyboard(add_menu=menu, back_menu="car", text="Добавить возмещение ущерба")))
async def service_history_list(update,state,bot_custom,repo):
    menu = "service_history"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    data = await state.get_data()
    car_id = data.get("car_id")
    service_history = await repo.service_history.get_all_active_service_history_where_id(car_id)
    for service in service_history:
        performer = await repo.performers.get_performer(performer_id=service.performer_id)
        if service.driver_id == 0:
            driver = "не назначен"
        else:
            driver = await repo.drivers.get_driver(driver_id=service.driver_id)
            driver = f"{driver.surname} {driver.name} {driver.patronymic}"
        post_time = service.date
        post_time_str = post_time.strftime("%d %B %Y")
        month = post_time.strftime('%B')
        bot_custom.messages[message.chat.id].append(await message.answer(f"Дата : {post_time_str.replace(month,month_names[month])}\nТип: {service.service_type}\nСумма: {service.amount}\nВодитель: {driver}\nИсполнитель: {performer.performer_name}\n", reply_markup=list_keyboard(record_id=service.record_id,menu=menu)))
    return bot_custom.messages[message.chat.id].append(await message.answer("Обслуживание", reply_markup=last_list_keyboard(add_menu=menu, back_menu="car", text="Добавить обслуживание")))
async def recovery_from_damages_list(update,state,bot_custom,repo):
    menu = "recovery_from_damages"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    data = await state.get_data()
    car_id = data.get("car_id")
    recovery_from_damages = await repo.recovery_from_damages.get_all_active_recovery_from_damage_where_id(car_id)
    for recovery in recovery_from_damages:
        performer = await repo.performers.get_performer(performer_id=recovery.payers_id)
        if recovery.driver_id==0:
            driver = "не назначен"
        else:
            driver = await repo.drivers.get_driver(driver_id=recovery.driver_id)
            driver = f"{driver.surname} {driver.name} {driver.patronymic}"
        post_time = recovery.date
        post_time_str = post_time.strftime("%d %B %Y")
        month = post_time.strftime('%B')
        bot_custom.messages[message.chat.id].append(await message.answer(f"Дата : {post_time_str.replace(month,month_names[month])}\nОписание: {recovery.description}\nСумма: {recovery.amount}\nВодитель: {driver}\nПлательщик: {performer.performer_name}\n", reply_markup=list_keyboard(record_id=recovery.record_id, menu=menu)))
    return bot_custom.messages[message.chat.id].append(await message.answer("Восстановление после ущерба", reply_markup=last_list_keyboard(add_menu=menu, back_menu="car", text="Добавить восстановление после ущерба")))
async def other_expenses_list(update,state,bot_custom,repo):
    menu = "other_expenses"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    data = await state.get_data()
    car_id = data.get("car_id")
    other_expenses = await repo.other_expenses.get_all_active_other_expenses_where_id(car_id)
    for expenditure in other_expenses:
        performer = await repo.performers.get_performer(performer_id=expenditure.performer_id)
        if expenditure.driver_id == 0:
            driver = "не назначен"
        else:
            driver = await repo.drivers.get_driver(driver_id=expenditure.driver_id)
            driver = f"{driver.surname} {driver.name} {driver.patronymic}"
        post_time = expenditure.date
        post_time_str = post_time.strftime("%d %B %Y")
        month = post_time.strftime('%B')
        bot_custom.messages[message.chat.id].append(await message.answer(f"Дата : {post_time_str.replace(month,month_names[month])}\nОписание: {expenditure.description}\nСумма: {expenditure.amount}\nВодитель: {driver}\nИсполнитель: {performer.performer_name}\n", reply_markup=list_keyboard(record_id=expenditure.record_id,menu=menu)))
    return bot_custom.messages[message.chat.id].append(await message.answer("Прочие раходы", reply_markup=last_list_keyboard(add_menu=menu, back_menu="car", text="Добавить расход")))
async def car_financial_calculation(update,bot_custom,repo,key,car_id = None,user_date = None):
    if isinstance(update, Message):
        message = update
    elif isinstance(update, CallbackQuery):
        message = update.message
    dates = []
    out_string = "Меню будет доступно,когда водитель внесёт первый платеж."
    if user_date:
        try:
            user_date = user_date.date()
        except:
            pass
        current_date = user_date
    else:
        current_date = await repo.rent_payment.get_first_date()
        try:
            current_date = current_date.date()
        except:
            return bot_custom.messages[message.chat.id].append(await message.answer(out_string, reply_markup=last_list_keyboard(back_menu=key)))
    if current_date:
        current_today = date.today()
        while current_date <= current_today:
            dates.append(current_date)
            try:
                current_date = current_date.replace(month=current_date.month + 1)
            except:
                current_date = current_date.replace(month=1)
                current_date = current_date.replace(year=current_date.year + 1)
        # dates.append(current_date)
    if car_id:
        total_sums_rent_payment_in_date  = {}
        total_sum_rent_payment = 0
        for udate in dates:
            total_sum = await repo.rent_payment.get_total_sum_with_date_where_car_id(car_id=car_id,user_date=udate)
            total_sum = total_sum if total_sum != None else 0
            total_sums_rent_payment_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_rent_payment += total_sum
        total_sum_compensation_for_damages_in_date = {}
        total_sum_compensation_for_damages = 0
        for udate in dates:
            total_sum = await repo.compensation_for_damages.get_total_sum_with_date_where_car_id(car_id=car_id,user_date=udate)
            total_sum = total_sum if total_sum != None else 0
            total_sum_compensation_for_damages_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_compensation_for_damages += total_sum
        total_sum_service_history_in_date = {}
        total_sum_service_history = 0
        for udate in dates:
            total_sum = await repo.service_history.get_total_sum_with_date_where_car_id(car_id=car_id,user_date=udate)
            total_sum = total_sum if total_sum != None else 0
            total_sum_service_history_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_service_history += total_sum
        total_sum_recovery_from_damages_in_date = {}
        total_sum_recovery_from_damages = 0
        for udate in dates:
            total_sum = await repo.recovery_from_damages.get_total_sum_with_date_where_car_id(car_id=car_id, user_date=udate)
            total_sum = total_sum if total_sum!=None else 0
            total_sum_recovery_from_damages_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_recovery_from_damages += total_sum
        total_sum_other_expenses_in_date = {}
        total_sum_other_expenses = 0
        for udate in dates:
            total_sum = await repo.other_expenses.get_total_sum_with_date_where_car_id(car_id=car_id, user_date=udate)
            total_sum = total_sum if total_sum!=None else 0
            total_sum_other_expenses_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_other_expenses += total_sum
        car = await repo.cars.get_car(car_id=car_id)
        car_cost = car.cost
    else:
        total_sums_rent_payment_in_date = {}
        total_sum_rent_payment = 0
        for udate in dates:
            total_sum = await repo.rent_payment.get_total_sum_with_date(user_date=udate)
            total_sum = total_sum if total_sum!=None else 0
            total_sums_rent_payment_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_rent_payment += total_sum
        total_sum_compensation_for_damages_in_date = {}
        total_sum_compensation_for_damages = 0
        for udate in dates:
            total_sum = await repo.compensation_for_damages.get_total_sum_with_date(user_date=udate)
            total_sum = total_sum if total_sum!=None else 0
            total_sum_compensation_for_damages_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_compensation_for_damages += total_sum
        total_sum_service_history_in_date = {}
        total_sum_service_history = 0
        for udate in dates:
            total_sum = await repo.service_history.get_total_sum_with_date(user_date=udate)
            total_sum = total_sum if total_sum!=None else 0
            total_sum_service_history_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_service_history += total_sum
        total_sum_recovery_from_damages_in_date = {}
        total_sum_recovery_from_damages = 0
        for udate in dates:
            total_sum = await repo.recovery_from_damages.get_total_sum_with_date(user_date=udate)
            total_sum = total_sum if total_sum!=None else 0
            total_sum_recovery_from_damages_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_recovery_from_damages += total_sum
        total_sum_other_expenses_in_date = {}
        total_sum_other_expenses = 0
        for udate in dates:
            total_sum = await repo.other_expenses.get_total_sum_with_date(user_date=udate)
            total_sum = total_sum if total_sum!=None else 0
            total_sum_other_expenses_in_date[f"{udate.month}.{udate.year}"] = total_sum
            total_sum_other_expenses += total_sum


        # Получение стоимости каждой машины
        cars = await repo.cars.get_all_active_cars()
        car_cost = sum(car.cost for car in cars)
    # Получение стоимости автомобиля из базы данных
    income = total_sum_rent_payment + total_sum_compensation_for_damages
    expenditure = total_sum_service_history + total_sum_recovery_from_damages +  total_sum_other_expenses
    profit = income - expenditure
    if total_sum_rent_payment:
        for udate in dates:
            month_year = f"{udate.month}.{udate.year}"
            rent_payment_in_date = total_sums_rent_payment_in_date[month_year]
            compensation_for_damages_in_date = total_sum_compensation_for_damages_in_date[month_year]
            service_history_in_date = total_sum_service_history_in_date[month_year]
            recovery_from_damages_in_date = total_sum_recovery_from_damages_in_date[month_year]
            other_expenses_in_date = total_sum_other_expenses_in_date[month_year]
            bot_custom.messages[message.chat.id].append(await message.answer(f"-----{month_year}-----\n"
                                                               f"Арендная плата: {rent_payment_in_date} \u20BD\n"
                                                               f"Возмещение ущерба: {compensation_for_damages_in_date} \u20BD\n"
                                                               f"Обслуживание: {service_history_in_date} \u20BD\n"
                                                               f"Восстановление после ущерба: {recovery_from_damages_in_date} \u20BD\n"
                                                               f"Прочие расходы: {other_expenses_in_date} \u20BD\n"
                                                               f"----------------\n"
                                                               f"Чистая прибыль: {rent_payment_in_date + compensation_for_damages_in_date - service_history_in_date - recovery_from_damages_in_date - other_expenses_in_date} \u20BD\n"))

        # if car_id:
        #     if user_date:
        #         min_date = user_date
        #         max_date = current_today
        #     else:
        #         min_date =  await repo.rent_payment.get_first_date_where_car_id(car_id=car_id)
        #         max_date = await repo.rent_payment.get_latest_date_where_car_id(car_id=car_id)
        # else:
        #     if user_date:
        #         min_date = user_date
        #         max_date = current_today
        #     else:
        #         min_date = await repo.rent_payment.get_first_date()
        #         max_date = await repo.rent_payment.get_latest_date()

        if car_id:
            min_date = await repo.rent_payment.get_first_date_where_car_id(car_id=car_id)
            max_date = await repo.rent_payment.get_latest_date_where_car_id(car_id=car_id)
        else:
            min_date = await repo.rent_payment.get_first_date()
            max_date = await repo.rent_payment.get_latest_date()

        if min_date:
            if car_cost:
                if min_date == max_date:
                    days_between = 1
                else:
                    days_between = (max_date - min_date).days
                day_profit = profit/days_between
                if profit < 0:
                    payback_days_to_string = "∞"
                    payback_date = "∞"
                else:
                    payback_days = int((car_cost-profit)//day_profit)
                    payback_days = 0 if payback_days < 0 else payback_days
                    payback_days_to_string = convert_days_to_years_months_days(payback_days)
                    try:
                        payback_date = (date.today() + timedelta(days=payback_days)).strftime('%d-%m-%Y')
                    except:
                        payback_date = "∞"
                if user_date:
                    out_string = "Для отображения прогнозной статистики выберите весь диапазон данных!"
                else:
                    out_string = f"Доход: {income} \u20BD\n" \
                                 f"Расход: {expenditure} \u20BD\n" \
                                 f"Чистая прибыль: {profit} \u20BD\n" \
                                 "Средняя прибыль за:\n" \
                                 f"  День: {round(day_profit,2)} \u20BD\n" \
                                 f"  Месяц: {round(day_profit * 31,2)} \u20BD\n" \
                                 f"  Год: {round(day_profit * 365,2)} \u20BD\n" \
                                 "Окупаемость:\n" \
                                 f"  ROI: {calculate_return_on_investment(profit,car_cost)} %\n" \
                                 f"  Срок: {payback_days_to_string} 👉 {payback_date}🗓\n"
            else:
                out_string = "В данный момент нет активных машин для составления прогнозной статистики!"
    return bot_custom.messages[message.chat.id].append(await message.answer(out_string, reply_markup=last_list_keyboard(back_menu=key)))
async def all_transfers(update,bot_custom,repo,key):
    if isinstance(update, Message):
        message = update
    elif isinstance(update, CallbackQuery):
        message = update.message
    drivers = await repo.drivers.get_all_active_drivers()
    end_date = date.today()
    start_date = end_date - timedelta(days=datetime.now().weekday())
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    if dates:
        for day_date in dates:
            first_date_weekday = day_date.weekday()+1
            day_date_str = day_date.strftime("%d %B %Y")
            month = day_date.strftime('%B')
            tmp_string = f"-----{day_date_str.replace(month, month_names[month])} | {weekdays_name_full[day_date.weekday()+1]}-----\n"
            out_string_final = tmp_string
            for driver in drivers:
                out_string_part = ""
                if driver.date_of_start_work.date() <= day_date and (not driver.date_of_termination or (driver.date_of_termination.date() > day_date)):
                    out_string_part += f"|👨 {driver.surname} {driver.name} "
                    weekdays_driver =  await repo.weekends.get_all_weekends_where_driver_id(driver_id=driver.driver_id)
                    try:
                        taxi_driver = await repo.taxi_company.get_object_where_driver_id(driver_id=driver.driver_id)
                        car_reg_number = taxi_driver.car.state_number
                        rent_ammount = taxi_driver.driver_rent
                    except:
                        try:
                            rent_payment_post = await repo.rent_payment.get_first_driver_payment(driver_id=driver.driver_id)
                            car_reg_number = rent_payment_post.car.state_number
                            rent_ammount = rent_payment_post.driver_rent
                        except:
                            car_reg_number = None
                    if first_date_weekday in weekdays_driver:
                        if car_reg_number:
                            out_string_part += f"| 🚖 {car_reg_number}| выходной 😴\n "
                        else:
                            out_string_part += f"| 🚖 отсутствует| выходной 😴\n"
                    else:
                        sum_rent_paymant_driver =  await repo.rent_payment.get_record_where_date_and_driver_id(driver_id=driver.driver_id,udate=day_date)
                        if sum_rent_paymant_driver:
                            out_string_part += f"| 🚖 {sum_rent_paymant_driver[0].car.state_number} "
                            sum_rent_paymant_driver = sum([float(record.amount) for record in sum_rent_paymant_driver])
                            out_string_part += f"| {sum_rent_paymant_driver}"
                            if sum_rent_paymant_driver == rent_ammount:
                                out_string_part += "\u20BD ✅\n"
                            else:
                                out_string_part += f" ≠ {rent_ammount} \u20BD ⚠️\n"
                        else:
                            if car_reg_number:
                                out_string_part += f"| 🚖 {car_reg_number} "
                                out_string_part += f"| не оплатил ‼️\n"
                            else:
                                out_string_part = ""
                if out_string_part:
                    out_string_final += out_string_part
            if out_string_final != tmp_string:
                bot_custom.messages[message.chat.id].append(await message.answer(out_string_final))
    return bot_custom.messages[message.chat.id].append(await message.answer("ПЕРЕВОДЫ 💳", reply_markup=last_list_keyboard(back_menu=key)))

async def rent_payment_list(update,state,bot_custom,repo):
    menu = "rent_payment"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    data = await state.get_data()
    driver_id = data.get("driver_id")
    match data.get("range"):
        case "week":
            rent_payment_posts = await repo.rent_payment.get_active_records_by_week(driver_id)
        case "month":
            rent_payment_posts = await repo.rent_payment.get_active_records_by_month(driver_id)
        case "all_time":
            rent_payment_posts = await repo.rent_payment.get_all_active_records(driver_id)
        case "user_range":
            rent_payment_posts = await repo.rent_payment.get_active_records_by_range(data.get("start_date"),data.get("end_date"),driver_id)
    for rent_post in rent_payment_posts:
        if rent_post.car_id == 0:
            car = "не назначен"
        else:
            car = await repo.cars.get_car(car_id=rent_post.car_id)
            car = f"{car.brand} {car.model} {car.state_number}"
        post_time = rent_post.date
        post_time_str = post_time.strftime("%d %B %Y")
        month = post_time.strftime('%B')
        bot_custom.messages[message.chat.id].append(await message.answer(f"Дата : {post_time_str.replace(month,month_names[month])}\nАвтомобиль: {car}\nСумма: {rent_post.amount}\nКомментарий: {rent_post.comment}\n", reply_markup=list_keyboard(record_id=rent_post.payment_id,menu=menu)))
    return bot_custom.messages[message.chat.id].append(await message.answer("Переводы", reply_markup=last_list_keyboard(add_menu=menu, back_menu="range", text="Добавить перевод")))
async def management_list(update,bot_custom,repo):
    menu = "management"
    if isinstance(update,Message):
        message = update
    elif isinstance(update,CallbackQuery):
        message = update.message
    taxi_managment = await repo.taxi_company.get_all_taxi_company()
    for management_pair in taxi_managment:
        car = await repo.cars.get_car(car_id=management_pair.car_id)
        if car.photo:
            photo_path = os.path.join(PHOTOS_DIR, "car", str(car.car_id), "facial_photo", f"{car.photo}.jpg")
            photo = FSInputFile(photo_path)
            bot_custom.messages[message.chat.id].append(await message.answer_photo(photo=photo, caption=f"Марка: {car.brand}\nМодель: {car.model}\nГод выпуска: {car.release_year}\nГос номер: {car.state_number}", reply_markup=management_keyboard(driver_id = management_pair.driver_id)))
        else:
            bot_custom.messages[message.chat.id].append(await message.answer(f"Марка: {car.brand}\nМодель: {car.model}\nГод выпуска: {car.release_year}\nГос номер: {car.state_number}", reply_markup=management_keyboard(driver_id=management_pair.driver_id)))
    return bot_custom.messages[message.chat.id].append(await message.answer("УПРАВЛЕНИЕ 🚕 - 👨", reply_markup=last_list_keyboard(add_menu=menu, back_menu="taxi_company", text="Добавить связку")))

@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext, bot_custom):
    await state.clear()
    logger.info(f"Бот был запущен пользователем: {message.chat.id}")
    return bot_custom.messages[message.chat.id].append(await message.answer('Привет! Я бот для управления таксопарком.', reply_markup=main_keyboard()))

"----------------------MAIN MENU------------------"
@user_router.callback_query(MainCallbackData.filter())
async def main_menu(query: CallbackQuery,bot_custom,repo,callback_data: MainCallbackData,config):
    await query.answer()
    main_menu = callback_data.main_menu
    if main_menu == "cars":
        logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню 'АВТОМОБИЛИ'")
        await car_list(query,bot_custom,repo)
    elif main_menu == "drivers":
        logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню 'ВОДИТЕЛИ'")
        await driver_list(query,bot_custom,repo)
    elif main_menu == "taxi_company":
        logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню 'ТАКСОПАРК'")
        if query.from_user.id in config.tg_bot.admin_ids:
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("ТАКСОПАРК", reply_markup=taxi_company_keyboard()))
        else:
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Доступ ограничен!",reply_markup=back_keyboard("main")))
"--------------------------------------------"

"----------------------ADD MENU------------------"
@user_router.callback_query(AddCallbackData.filter())
async def add_menu(query: CallbackQuery,state: FSMContext,bot_custom,callback_data: AddCallbackData,repo):
    await query.answer()
    menu = callback_data.add_menu
    match menu:
        case "car":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите марку автомобиля",reply_markup=back_keyboard("car_list")))
            return await state.set_state(AddCar.Brand)
        case "driver":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите фамилию", reply_markup=back_keyboard("driver_list")))
            return await state.set_state(AddDriver.Surname)
        case "rent_payment":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            try:
                data = await state.get_data()
                taxi_company_record = await repo.taxi_company.get_object_where_driver_id(driver_id=data.get('driver_id'))
                bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
                return await state.set_state(AddRentPayment.Date)
            except:
                logger.error(f"Пользователь '{query.message.chat.id}' пожалуйста, создайте связь с данным водителем в таксопарке")
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Пожалуйста, создайте связь с данным водителем в таксопарке.", reply_markup=back_keyboard("driver")))
        case "service_history":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(AddServiceHistory.Date)
        case "compensation_for_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(AddCompensationForDamages.Date)
        case "recovery_from_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(AddRecoveryFromDamages.Date)
        case "other_expenses":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(AddOtherExpenses.Date)
        case "service_history__performer" |"update_service_history__performer" |"other_expenses__performer"|"update_other_expenses__performer":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите название исполнителя", reply_markup=back_keyboard("performer_list")))
            return await state.set_state(AddPerformer.PerformerName)
        case "compensation_for_damages__performer"|"update_compensation_for_damages__performer"|"recovery_from_damages__performer"|"update_recovery_from_damages__performer":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите название плательщика", reply_markup=back_keyboard("performer_list")))
            return await state.set_state(AddPerformer.PerformerName)
        case "management":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            return await car_list(query, bot_custom, repo,menu="management")
        case "inspections":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте медиа файлы"))
            return await state.set_state(AddMedia.Inspections)
        case "media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте медиа файлы"))
            return await state.set_state(AddMedia.Media)
        case "service_history_media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте медиа файлы"))
            return await state.set_state(AddMedia.MediaServiceHistory)
        case "compensation_for_damages_media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте медиа файлы"))
            return await state.set_state(AddMedia.MediaCompensationForDamages)
        case "recovery_from_damages_media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте медиа файлы"))
            return await state.set_state(AddMedia.MediaRecoveryFromDamages)
        case "other_expenses_media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавлениe {menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте медиа файлы"))
            return await state.set_state(AddMedia.MediaOtherExpenses)
"--------------------------------------------"

"----------------------ADD PERFORMER------------------"
@user_router.message(AddPerformer.PerformerName)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    performer_name = message.text
    if performer_name.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{performer_name}' Вы ввели команду!Пожалуйста введите название исполнителя!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!Пожалуйста введите название исполнителя!"))
    elif len(performer_name) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{performer_name}' Ошибка! Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    menu = data.get("performer_menu")
    try:
        await repo.performers.get_create_update_performer(performer_name=performer_name)
        logger.info(f"Пользователь '{message.chat.id}' добавил исполнителя {performer_name}")
    except:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Не получилось добавить исполнителя {performer_name}")
    return await performer_list(message,bot_custom,repo,menu= menu)
"--------------------------------------------"

"----------------------ADD CAR------------------"
@user_router.message(AddCar.FacialPhoto)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    if message.video:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Вы отправили видео!Нужно отправить фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Вы отправили видео!\nНужно отправить фото!"))
    elif album:
        await album[0].delete()
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте одно фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте одно фото!"))
    elif message.text or (not message.photo):
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте фото!"))
    else:
        data = await state.get_data()
        car_id = data.get("car_id")
        car_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), "facial_photo")
        os.makedirs(car_dir, exist_ok=True)
        if os.listdir(car_dir):
            for file in os.listdir(car_dir):
                file_split = file.split(".")
                if not file_split[0].endswith("_archive"):
                    # Добавление окончания archive к файлу
                    new_file = file_split[0] + "_archive." + file_split[1]
                    # Переименование файла
                    os.rename(os.path.join(car_dir, file), os.path.join(car_dir, new_file))
        try:
            photos = message.photo
            photo = photos[-1]
            file_id = photo.file_id
            await repo.cars.get_create_update_car(car_id=car_id,
                photo=file_id,
            )
            media_path = os.path.join(car_dir, f'{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            logger.info(f"Пользователь '{message.chat.id}' Фото к автомобилю '{car_id}' успешно добавлено!")
            bot_custom.messages[message.chat.id].append(message := await message.answer(f"Фото к автомобилю '{car_id}' успешно добавлено!"))
        except:
            logger.error(f"Пользователь '{message.chat.id}' Произошла ошибка при добавлении фото к автомобилю '{car_id}'!")
            bot_custom.messages[message.chat.id].append(message := await message.answer("Произошла Ошибка!"))
        await asyncio.sleep(2)
    await state.set_state()
    await message.delete()
    return await car_list(message, bot_custom, repo)

@user_router.message(AddCar.Brand)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    brand = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{brand}' Ошибка! Вы ввели команду!Пожалуйста введите марку автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите марку автомобиля!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{brand}' Ошибка! Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(brand=brand)
    logger.info(f"Пользователь '{message.chat.id}' ввел марку автомобиля '{brand}'")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите модель автомобиля"))
    return await state.set_state(AddCar.Model)

@user_router.message(AddCar.Model)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    model = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{model}' Ошибка! Вы ввели команду!Пожалуйста введите модель автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите модель автомобиля!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{model}' Ошибка! Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(model=model)
    logger.info(f"Пользователь '{message.chat.id}' ввел модель автомобиля: '{model}'")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите год выпуска автомобиля"))
    return await state.set_state(AddCar.ReleaseYear)

@user_router.message(AddCar.ReleaseYear)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    try:
        release_year = int(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{release_year}' Ошибка! Вы ввели команду!Пожалуйста введите год выпуска автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите год выпуска автомобиля!"))
    elif len(release_year) > 4:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{release_year}' Ошибка! Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(release_year=release_year)
    logger.info(f"Пользователь '{message.chat.id}' выбрал год выпуска автомобиля: '{release_year}'")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите гос номер автомобиля"))
    return await state.set_state(AddCar.StateNumber)

@user_router.message(AddCar.StateNumber)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    state_number = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{state_number}' Ошибка! Вы ввели команду!Пожалуйста введите гос номер автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите гос номер автомобиля!"))
    elif len(message.text) > 15:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{state_number}' Ошибка! Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(state_number=state_number)
    logger.info(f"Пользователь '{message.chat.id}' ввел гос номер автомобиля: '{state_number}'")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите стоимость автомобиля"))
    return await state.set_state(AddCar.Cost)

@user_router.message(AddCar.Cost)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        cost = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Вы ввели команду!Пожалуйста введите стоимость автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость автомобиля!"))
    await state.update_data(cost=cost)
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость автомобиля {cost}")
    data = await state.get_data()
    try:
        car = await repo.cars.get_create_update_car(brand= data.get('brand'),
            model= data.get('model'),
            release_year=data.get('release_year'),
            state_number=data.get('state_number'),
            cost=data.get('cost'),
        )
        logger.info(f"Пользователь '{message.chat.id}' добавил автомобиль {car.car_id}")
    except:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка при добавлении автомобиля!")
    await state.update_data(car_id=car.car_id)
    return bot_custom.messages[message.chat.id].append(await message.answer("Желаете добавить лицевое фото машины?", reply_markup=confirmation_keyboard(action="add_car_facial_photo")))
"--------------------------------------------"

"----------------------ADD COMPENSATION FOR DAMAGE------------------"

@user_router.message(AddCompensationForDamages.Description)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    description = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Ошибка! Вы ввели команду!Пожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите описание!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Ошибка! Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(description=description)
    logger.info(f"Пользователь '{message.chat.id}' ввел описание {description}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите стоимость возмещения ущерба"))
    return await state.set_state(AddCompensationForDamages.Amount)

@user_router.message(AddCompensationForDamages.Amount)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Ошибка! Вы ввели команду!Пожалуйста введите стоимость возмещения ущерба!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость возмещения ущерба!"))
    await state.update_data(amount=amount)
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость {amount}")
    await state.set_state(AddCompensationForDamages.PayersId)
    menu = "compensation_for_damages__performer"
    await state.update_data(performer_menu=menu)
    return await performer_list(message,bot_custom,repo,menu= menu)

"--------------------------------------------"

"----------------------ADD SERVICE HISTORY------------------"

@user_router.message(AddServiceHistory.ServiceType)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    service_type = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{service_type}' Вы ввели команду!Пожалуйста введите тип обслуживания!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите тип обслуживания!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{service_type}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(service_type=service_type)
    logger.info(f"Пользователь '{message.chat.id}' ввел тип обслуживания {service_type}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите стоимость обслуживания"))
    return await state.set_state(AddServiceHistory.Amount)

@user_router.message(AddServiceHistory.Amount)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость обслуживания!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость обслуживания!"))
    await state.update_data(amount=amount)
    await state.set_state(AddServiceHistory.PerformerId)
    logger.info(f"Пользователь '{message.chat.id}' ввел тип обслуживания {amount}")
    menu = "service_history__performer"
    await state.update_data(performer_menu=menu)
    return await performer_list(message,bot_custom,repo,menu= menu)

"--------------------------------------------"

"----------------------ADD RECOVERY FROM DAMAGE------------------"

@user_router.message(AddRecoveryFromDamages.Description)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    description = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Вы ввели команду!Пожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите описание!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(description=description)
    logger.info(f"Пользователь '{message.chat.id}' ввел описание {description}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите стоимоcть восстановления после ущерба"))
    return await state.set_state(AddRecoveryFromDamages.Amount)

@user_router.message(AddRecoveryFromDamages.Amount)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!\nПожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!\nПожалуйста введите стоимость восстановления после ущерба!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость восстановления после ущерба!"))
    await state.update_data(amount=amount)
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость {amount}")
    await state.set_state(AddRecoveryFromDamages.PayersId)
    menu = "recovery_from_damages__performer"
    await state.update_data(performer_menu=menu)
    return await performer_list(message,bot_custom,repo,menu= menu)

"--------------------------------------------"

"----------------------ADD OTHER EXPENSES------------------"

@user_router.message(AddOtherExpenses.Description)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    description = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Вы ввели команду!Пожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите описание!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(description=description)
    logger.info(f"Пользователь '{message.chat.id}' ввел описание {description}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите стоимость расходов"))
    return await state.set_state(AddOtherExpenses.Amount)

@user_router.message(AddOtherExpenses.Amount)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость расходов!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость расходов!"))
    await state.update_data(amount=amount)
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость {amount}")
    await state.set_state(AddOtherExpenses.PerformerId)
    menu = "other_expenses__performer"
    await state.update_data(performer_menu=menu)
    return await performer_list(message,bot_custom,repo,menu= menu)

"--------------------------------------------"

"----------------------ADD RENT PAYMENT------------------"

@user_router.message(AddRentPayment.Сomment)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    comment = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{comment}' Вы ввели команду!Пожалуйста введите комментарий!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите комментарий!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{comment}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(comment=comment)
    logger.info(f"Пользователь '{message.chat.id}' ввел комментарий {comment}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите сумму"))
    return await state.set_state(AddRentPayment.Amount)

@user_router.message(AddRentPayment.Amount)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость расходов!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость расходов!"))
    await state.update_data(amount=amount)
    data = await state.get_data()
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость расходов {amount}")
    taxi_company_record = await repo.taxi_company.get_object_where_driver_id(driver_id=data.get('driver_id'))
    car_id = taxi_company_record.car_id
    driver_rent = taxi_company_record.driver_rent
    try:
        rent_paym =await repo.rent_payment.get_create_update_rent_payment(car_id=car_id,
            driver_id=data.get('driver_id'),
            date=datetime.strptime(data.get('date'), "%Y-%m-%d %H:%M:%S"),
            comment=data.get('comment'),
            amount=data.get('amount'),
            driver_rent=driver_rent,
        )
        logger.info(f"Пользователь '{message.chat.id}' добавил перевод {rent_paym.payment_id}")
    except:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка при добавлении перевода!")

    return await rent_payment_list(message, state, bot_custom, repo)

"--------------------------------------------"


"----------------------ADD DRIVER------------------"

@user_router.message(AddDriver.FacialPhoto)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    if message.video:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Вы отправили видео!Нужно отправить фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Вы отправили видео!\nНужно отправить фото!"))
    elif album:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте одно фото!")
        await album[0].delete()
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте одно фото!"))
    elif message.text or (not message.photo):
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте фото!"))
    else:
        data = await state.get_data()
        driver_id = data.get("driver_id")
        driver_dir = os.path.join(PHOTOS_DIR, "driver", str(driver_id), "facial_photo")
        os.makedirs(driver_dir, exist_ok=True)
        if os.listdir(driver_dir):
            for file in os.listdir(driver_dir):
                file_split = file.split(".")
                if not file_split[0].endswith("_archive"):
                    # Добавление окончания archive к файлу
                    new_file = file_split[0] + "_archive." + file_split[1]
                    # Переименование файла
                    os.rename(os.path.join(driver_dir, file), os.path.join(driver_dir, new_file))
        try:
            photos = message.photo
            photo = photos[-1]
            file_id = photo.file_id
            await repo.drivers.get_create_update_driver(driver_id=driver_id,
                photo=file_id,
            )
            media_path = os.path.join(driver_dir, f'{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            logger.info(f"Пользователь '{message.chat.id}' фото к водителю '{driver_id}' успешно добавлено!")
            bot_custom.messages[message.chat.id].append(message := await message.answer("Фото успешно добавлено!"))
        except:
            logger.error(f"Пользователь '{message.chat.id}' Произошла ошибка при добавлении фото к водителю '{driver_id}'!")
            bot_custom.messages[message.chat.id].append(message := await message.answer("Произошла Ошибка!"))
        await asyncio.sleep(2)
    await state.set_state()
    await message.delete()
    return await driver_list(message,bot_custom,repo)

@user_router.message(AddDriver.Surname)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    surname = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{surname}' Вы ввели команду!\nПожалуйста введите фамилию!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите фамилию!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{surname}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(surname=surname)
    logger.info(f"Пользователь '{message.chat.id}' ввел фамилию {surname}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите имя"))
    return await state.set_state(AddDriver.Name)

@user_router.message(AddDriver.Name)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    name = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{name}' Вы ввели команду!\nПожалуйста введите имя!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите имя!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{name}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(name=name)
    logger.info(f"Пользователь '{message.chat.id}' ввел имя {name}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите отчество"))
    return await state.set_state(AddDriver.Patronymic)

@user_router.message(AddDriver.Patronymic)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    patronymic = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{patronymic}' Вы ввели команду!\nПожалуйста введите отчество!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите отчество!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{patronymic}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(patronymic=patronymic)
    logger.info(f"Пользователь '{message.chat.id}' ввел отчество {patronymic}")
    bot_custom.messages[message.chat.id].append(await message.answer("Выберите дату рождения", reply_markup=await DialogCalendar().start_calendar()))
    return await state.set_state(AddDriver.Birthdate)

@user_router.message(AddDriver.ContactInformation)
async def answer_qa(message: Message,state: FSMContext,bot_custom):
    contact_information = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{contact_information}' Вы ввели команду!\nПожалуйста введите контактную информацию!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите контактную информацию!"))
    elif len(message.text) > 100:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{contact_information}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(contact_information=contact_information)
    logger.info(f"Пользователь '{message.chat.id}' ввел контактную информацию {contact_information}")
    bot_custom.messages[message.chat.id].append(await message.answer("Введите дополнительную информацию"))
    return await state.set_state(AddDriver.AdditionalInformation)

@user_router.message(AddDriver.AdditionalInformation)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    additional_information = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{additional_information}' Вы ввели команду!\nПожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите дополнительную информацию!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{additional_information}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    await state.update_data(additional_information=additional_information)
    logger.info(f"Пользователь '{message.chat.id}' ввел дополнительную информацию {additional_information}")
    data = await state.get_data()
    try:
        driver = await repo.drivers.get_create_update_driver(surname=data.get('surname'),
            name=data.get('name'),
            patronymic=data.get('patronymic'),
            birthdate= datetime.strptime(data.get('birthdate'), "%Y-%m-%d %H:%M:%S"),
            date_of_start_work=datetime.strptime(data.get('date_of_start_work'), "%Y-%m-%d %H:%M:%S"),
            contact_information=data.get('contact_information'),
            additional_information=data.get('additional_information'),
        )
        logger.info(f"Пользователь '{message.chat.id}' добавил водителя '{driver.driver_id}'")
    except:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка при добавлении водителя!")
    await state.update_data(driver_id=driver.driver_id)
    return bot_custom.messages[message.chat.id].append(await message.answer("Желаете добавить лицевое фото водителя?", reply_markup=confirmation_keyboard(action="add_driver_facial_photo")))

"--------------------------------------------"

"----------------------ADD MANAGEMENT------------------"

@user_router.message(AddManagement.DriverRent)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        driver_rent = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{driver_rent}' Вы ввели команду!\nПожалуйста введите размер арендной платы!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите размер арендной платы!"))
    data = await state.get_data()
    logger.info(f"Пользователь '{message.chat.id}' ввел размер арендной платы {driver_rent}")
    try:
        taxi_comp = await repo.taxi_company.get_create_update_taxi_company(car_id=data.get('car_id'),
            driver_id=data.get('driver_id'),
            driver_rent=driver_rent,
        )
        logger.info(f"Пользователь '{message.chat.id}' добавил саязку '{taxi_comp.record_id}'")
    except:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка при добавлении связки!")
    await state.set_state()
    return await management_list(message, bot_custom, repo)
"--------------------------------------------"

"----------------------CHANGE RENT------------------"

@user_router.message(UpdateDriverInManagement.DriverRent)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        driver_rent = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{driver_rent}' Вы ввели команду!\nПожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите размер арендной платы!"))
    data = await state.get_data()
    driver_id = data.get('driver_id')
    try:
        taxi_com = await repo.taxi_company.set_driver_rent_where_driver_id(driver_id=driver_id,
            driver_rent=driver_rent,
        )
        logger.info(f"Пользователь '{message.chat.id}' изменил арендную плату на '{driver_rent}' в связке {taxi_com.record_id}")
    except:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка при изменении арендной платы на '{driver_rent}' в связке {taxi_com.record_id}")
    await state.set_state()
    driver_id = data.get("driver_id")
    driver = await repo.drivers.get_driver(driver_id=driver_id)
    birthday = driver.birthdate
    start_work_date = driver.date_of_start_work
    driver_rent = await repo.taxi_company.get_driver_rent_where_driver_id(driver_id=driver_id)
    if driver.photo:
        photo_path = os.path.join(PHOTOS_DIR, "driver", str(driver.driver_id), "facial_photo", f"{driver.photo}.jpg")
        photo = FSInputFile(photo_path)
        bot_custom.messages[message.chat.id].append(await message.answer_photo(photo=photo, caption=f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}\n\nАрендная плата: {driver_rent}"))
        return bot_custom.messages[message.chat.id].append(await message.answer("Изменить:", reply_markup=driver_in_management_keyboard(key="management")))
    else:
        bot_custom.messages[message.chat.id].append(await message.answer(f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}\n\nАрендная плата: {driver_rent}"))
        return bot_custom.messages[message.chat.id].append(await message.answer("Изменить:", reply_markup=driver_in_management_keyboard(key="management")))


"--------------------------------------------"


"------------------LIST----------------------"
@user_router.callback_query(ListCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext,callback_data: ListCallbackData,bot_custom,repo):
    record_id = callback_data.record_id
    menu = callback_data.menu
    data = await state.get_data()
    match menu:
        case "car":
            await state.update_data(car_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=car_keyboard()))
        case "driver":
            await state.update_data(driver_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=driver_keyboard()))
        case "compensation_for_damages__performer" | "service_history__performer"| "recovery_from_damages__performer"|"other_expenses__performer":
            await state.update_data(performer_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с исполнителем', reply_markup=performer_keyboard(menu)))
        case "rent_payment":
            await state.update_data(payment_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=rent_payment_keyboard()))
        case "management":
            await state.update_data(car_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return await driver_list(query,bot_custom,repo,menu = "management__driver")
        case "management__driver":
            await state.update_data(driver_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer('Введите размер арендной платы'))
            return await state.set_state(AddManagement.DriverRent)
        case "compensation_for_damages":
            await state.update_data(compensation_for_damages_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=compensation_for_damages_keyboard()))
        case "service_history":
            await state.update_data(service_history_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=service_history_keyboard()))
        case "recovery_from_damages":
            await state.update_data(recovery_from_damages_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=recovery_from_damages_keyboard()))
        case "other_expenses":
            await state.update_data(other_expenses_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=other_expenses_keyboard()))
        case "update_service_history__performer":
            await state.update_data(performer_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с исполнителем', reply_markup=performer_keyboard(data.get("performer_menu"))))
        case "update_compensation_for_damages__performer":
            await state.update_data(performer_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с плательщиком', reply_markup=performer_keyboard(data.get("performer_menu"))))
        case "update_recovery_from_damages__performer":
            await state.update_data(performer_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с плательщиком', reply_markup=performer_keyboard(data.get("performer_menu"))))
        case "update_other_expenses__performer":
            await state.update_data(performer_id=record_id)
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с исполнителем', reply_markup=performer_keyboard(data.get("performer_menu"))))


"--------------------------------------------"

"------------------MEDIA----------------------"
@user_router.message(AddMedia.Inspections)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    data = await state.get_data()
    car_id = data.get("car_id")
    try:
        driver_id = await repo.taxi_company.get_driver_id_where_car_id(car_id=car_id)
    except:
        driver_id = 0
    date_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), "inspections", message.date.strftime('%d_%m_%Y'))
    os.makedirs(date_dir, exist_ok=True)
    if album:
        tmp_mess = []
        for i in range(len(album)-1,-1,-1):
            try:
                await album[i].delete()
            except:
                pass
            if album[i].video:
                file_id = album[i].video.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                    logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
                    logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
            elif album[i].photo:
                photos = album[i].photo
                photo = photos[-1]
                file_id = photo.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                    logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
                    logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        for mess in tmp_mess:
            await mess.delete()
    elif message.video:
        file_id = message.video.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    elif message.photo:
        try:
            photos = message.photo
            photo = photos[-1]
            file_id = photo.file_id
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    return await inspections_list(message,state,bot_custom,repo)
@user_router.message(AddMedia.Media)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    data = await state.get_data()
    driver_id = data.get("driver_id")
    try:
        car_id = await repo.taxi_company.get_car_id_where_driver_id(driver_id=driver_id)
    except:
        car_id = 0
    date_dir = os.path.join(PHOTOS_DIR, "driver", str(driver_id), "media", message.date.strftime('%d_%m_%Y'))
    os.makedirs(date_dir, exist_ok=True)
    if album:
        tmp_mess = []
        for i in range(len(album)-1,-1,-1):
            try:
                await album[i].delete()
            except:
                pass
            if album[i].video:
                file_id = album[i].video.file_id
                try:
                    media_path = os.path.join(date_dir, f'{car_id}_{file_id}.mp4')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
            elif album[i].photo:
                photos = album[i].photo
                photo = photos[-1]
                file_id = photo.file_id
                try:
                    media_path = os.path.join(date_dir, f'{car_id}_{file_id}.jpg')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
        await asyncio.sleep(2)
        for mess in tmp_mess:
            await mess.delete()
    elif message.video:
        file_id = message.video.file_id
        try:
            media_path = os.path.join(date_dir, f'{car_id}_{file_id}.mp4')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    elif message.photo:
        photos = message.photo
        photo = photos[-1]
        file_id = photo.file_id
        try:
            media_path = os.path.join(date_dir, f'{car_id}_{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    return await media_list(message,state,bot_custom,repo)
@user_router.message(AddMedia.MediaServiceHistory)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    data = await state.get_data()
    car_id = data.get("car_id")
    record_id = data.get("service_history_id")
    try:
        driver_id = await repo.taxi_company.get_driver_id_where_car_id(car_id=car_id)
    except:
        driver_id = 0
    date_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), "service_history",str(record_id),message.date.strftime('%d_%m_%Y'))
    os.makedirs(date_dir, exist_ok=True)
    if album:
        tmp_mess = []
        for i in range(len(album)-1,-1,-1):
            try:
                await album[i].delete()
            except:
                pass
            if album[i].video:
                file_id = album[i].video.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
            elif album[i].photo:
                photos = album[i].photo
                photo = photos[-1]
                file_id = photo.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
        await asyncio.sleep(2)
        for mess in tmp_mess:
            await mess.delete()
    elif message.video:
        file_id = message.video.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    elif message.photo:
        photos = message.photo
        photo = photos[-1]
        file_id = photo.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    return await expenses_list(message,state,bot_custom,repo)
@user_router.message(AddMedia.MediaCompensationForDamages)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    data = await state.get_data()
    car_id = data.get("car_id")
    record_id = data.get("compensation_for_damages_id")
    try:
        driver_id = await repo.taxi_company.get_driver_id_where_car_id(car_id=car_id)
    except:
        driver_id = 0
    date_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), "compensation_for_damages",str(record_id), message.date.strftime('%d_%m_%Y'))
    os.makedirs(date_dir, exist_ok=True)
    if album:
        tmp_mess = []
        for i in range(len(album)-1,-1,-1):
            try:
                await album[i].delete()
            except:
                pass
            if album[i].video:
                file_id = album[i].video.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
            elif album[i].photo:
                photos = album[i].photo
                photo = photos[-1]
                file_id = photo.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
        await asyncio.sleep(2)
        for mess in tmp_mess:
            await mess.delete()
    elif message.video:
        file_id = message.video.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    elif message.photo:
        photos = message.photo
        photo = photos[-1]
        file_id = photo.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    return await expenses_list(message,state,bot_custom,repo)
@user_router.message(AddMedia.MediaRecoveryFromDamages)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    data = await state.get_data()
    car_id = data.get("car_id")
    record_id = data.get("recovery_from_damages_id")
    try:
        driver_id = await repo.taxi_company.get_driver_id_where_car_id(car_id=car_id)
    except:
        driver_id = 0
    date_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), "recovery_from_damages", str(record_id),message.date.strftime('%d_%m_%Y'))
    os.makedirs(date_dir, exist_ok=True)
    if album:
        tmp_mess = []
        for i in range(len(album)-1,-1,-1):
            try:
                await album[i].delete()
            except:
                pass
            if album[i].video:
                file_id = album[i].video.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
            elif album[i].photo:
                photos = album[i].photo
                photo = photos[-1]
                file_id = photo.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
        await asyncio.sleep(2)
        for mess in tmp_mess:
            await mess.delete()
    elif message.video:
        file_id = message.video.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    elif message.photo:
        photos = message.photo
        photo = photos[-1]
        file_id = photo.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    return await expenses_list(message,state,bot_custom,repo)
@user_router.message(AddMedia.MediaOtherExpenses)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    data = await state.get_data()
    car_id = data.get("car_id")
    record_id = data.get("other_expenses_id")
    try:
        driver_id = await repo.taxi_company.get_driver_id_where_car_id(car_id=car_id)
    except:
        driver_id = 0
    date_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), "other_expenses",str(record_id),message.date.strftime('%d_%m_%Y'))
    os.makedirs(date_dir, exist_ok=True)
    if album:
        tmp_mess = []
        for i in range(len(album)-1,-1,-1):
            try:
                await album[i].delete()
            except:
                pass
            file_id = album[i].video.file_id
            if album[i].video:
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
            elif album[i].photo:
                photos = album[i].photo
                photo = photos[-1]
                file_id = photo.file_id
                try:
                    media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
                    file_info = await message.bot.get_file(file_id)
                    file_path = file_info.file_path
                    await message.bot.download_file(file_path, media_path)
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ✅"))
                except:
                    tmp_mess.append(message := await message.answer(f"'{file_id}' ❌"))
        await asyncio.sleep(2)
        for mess in tmp_mess:
            await mess.delete()
    elif message.video:
        file_id = message.video.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.mp4')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    elif message.photo:
        photos = message.photo
        photo = photos[-1]
        file_id = photo.file_id
        try:
            media_path = os.path.join(date_dir, f'{driver_id}_{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            message = await message.answer(f"'{file_id}' ✅")
            logger.info(f"Пользователь '{message.chat.id}' сохранил медиа  '{file_id}'")
        except:
            message = await message.answer(f"'{file_id}' ❌")
            logger.error(f"Пользователь '{message.chat.id}' Ошибка! При сохранении медиа  '{file_id}'")
        await asyncio.sleep(2)
        await message.delete()
    return await expenses_list(message,state,bot_custom,repo)
"--------------------------------------------"

"------------------REMOVE MEDIA----------------------"
@user_router.callback_query(RemoveMediaCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: RemoveMediaCallbackData, bot_custom, repo):
    menu = callback_data.menu
    record_id = callback_data.record_id
    await state.update_data(remove_record_id = record_id)
    match menu:
        case "inspections":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удеаления медиа '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить запись осмотра?", reply_markup=confirmation_keyboard(action="remove_inspection")))
        case "media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удеаления медиа '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить медиа запись?", reply_markup=confirmation_keyboard(action="remove_media")))
        case "compensation_for_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удеаления медиа '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить медиа запись?", reply_markup=confirmation_keyboard(action="remove_media_compensation_for_damages")))
        case "service_history":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удеаления медиа '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить медиа запись?", reply_markup=confirmation_keyboard(action="remove_media_service_history")))
        case "recovery_from_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удеаления медиа '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить медиа запись?", reply_markup=confirmation_keyboard(action="remove_media_recovery_from_damages")))
        case "other_expenses":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удеаления медиа '{menu}'- id запси -'{record_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить медиа запись?", reply_markup=confirmation_keyboard(action="remove_media_other_expenses")))
        case _:
            pass
"--------------------------------------------"

"------------------CAR----------------------"
@user_router.callback_query(CarCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: CarCallbackData, bot_custom, repo,config):
    menu = callback_data.menu
    match menu:
        case "inspections":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(menu=menu,back_menu="car")))
        case "compensation_for_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
            return await compensation_for_damages_list(query,state, bot_custom, repo)
        case "service_history":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
            return await service_history_list(query, state, bot_custom, repo)
        case "recovery_from_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
            return await recovery_from_damages_list(query, state, bot_custom, repo)
        case "other_expenses":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
            return await other_expenses_list(query, state, bot_custom, repo)
        case "profitability":
            if query.from_user.id in config.tg_bot.admin_ids:
                logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=profit_range_keyboard(menu="car_menu")))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer("Доступ ограничен!", reply_markup=back_keyboard("car")))
        case "change":
            if query.from_user.id in config.tg_bot.admin_ids:
                logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_car_keyboard()))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer("Доступ ограничен!", reply_markup=back_keyboard("car")))
        case "remove":
            if query.from_user.id in config.tg_bot.admin_ids:
                logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню автомобиля - '{menu}'")
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить автомобиль?", reply_markup=confirmation_keyboard(action="remove_car")))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer("Доступ ограничен!", reply_markup=back_keyboard("car")))
        case _:
            pass
"--------------------------------------------"

"------------------DRIVER----------------------"
@user_router.callback_query(DriverCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext,callback_data: DriverCallbackData,bot_custom,repo,config):
    menu = callback_data.menu
    match menu:
        case "media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню водителя - '{menu}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(menu=menu,back_menu="driver")))
        case "translations":
            if query.from_user.id in config.tg_bot.admin_ids:
                logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню водителя - '{menu}'")
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(back_menu="driver",menu="translations")))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer("Доступ ограничен!", reply_markup=back_keyboard("driver")))
        case "change":
            if query.from_user.id in config.tg_bot.admin_ids:
                logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню водителя - '{menu}'")
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_driver_keyboard()))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer("Доступ ограничен!", reply_markup=back_keyboard("driver")))
        case "dismiss":
            if query.from_user.id in config.tg_bot.admin_ids:
                logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню водителя - '{menu}'")
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите уволить водителя?", reply_markup=confirmation_keyboard(action="dismiss_driver")))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer("Доступ ограничен!", reply_markup=back_keyboard("driver")))
        case _:
            pass
"--------------------------------------------"

"------------------PERFORMER----------------------"
@user_router.callback_query(PerformerCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext,callback_data: PerformerCallbackData,bot_custom,repo):
    action = callback_data.action
    data = await state.get_data()
    menu = data.get('performer_menu')
    match action:
        case "choose":
            try:
                driver_id = await repo.taxi_company.get_driver_id_where_car_id(car_id=data.get('car_id'))
            except:
                driver_id = 0
            match menu:
                case "service_history__performer":
                    try:
                        serv_his = await repo.service_history.get_create_update_service_history(car_id=data.get('car_id'),
                            driver_id=driver_id,
                            date=datetime.strptime(data.get('date'), "%Y-%m-%d %H:%M:%S"),
                            service_type=data.get('service_type'),
                            amount=data.get('amount'),
                            performer_id=data.get('performer_id'),
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' создал запись обслуживания - '{serv_his.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при создании записи обслуживания")
                    return await service_history_list(query, state, bot_custom, repo)
                case "compensation_for_damages__performer":
                    try:
                        compensation_for_dam =await repo.compensation_for_damages.get_create_update_compensation_for_damages(car_id= data.get('car_id'),
                            driver_id= driver_id,
                            date=datetime.strptime(data.get('date'), "%Y-%m-%d %H:%M:%S"),
                            description=data.get('description'),
                            amount=data.get('amount'),
                            payers_id=data.get('performer_id'),
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' создал запись возмещения ущерба - '{compensation_for_dam.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при создании записи возмещения ущерба")
                    return await compensation_for_damages_list(query,state, bot_custom, repo)
                case "recovery_from_damages__performer":
                    try:
                        compensation_for_dam = await repo.recovery_from_damages.get_create_update_recovery_from_damages(car_id=data.get('car_id'),
                            driver_id=driver_id,
                            date=datetime.strptime(data.get('date'), "%Y-%m-%d %H:%M:%S"),
                            description=data.get('description'),
                            amount=data.get('amount'),
                            payers_id=data.get('performer_id'),
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' создал запись восстановление после ущерба - '{compensation_for_dam.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при создании записи восстановление после ущерба")
                    return await recovery_from_damages_list(query, state, bot_custom, repo)
                case "other_expenses__performer":
                    try:
                        other_expen = await repo.other_expenses.get_create_update_other_expenses(car_id=data.get('car_id'),
                            driver_id=driver_id,
                            date=datetime.strptime(data.get('date'), "%Y-%m-%d %H:%M:%S"),
                            description=data.get('description'),
                            amount=data.get('amount'),
                            performer_id=data.get('performer_id'),
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' создал запись прочих расходов - '{other_expen.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при создании записи прочих расходов")
                    return await other_expenses_list(query, state, bot_custom, repo)
                case "update_service_history__performer":
                    try:
                        serv_his = await repo.service_history.get_create_update_service_history(record_id=data.get('service_history_id'),
                            performer_id=data.get('performer_id')
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' изменил запись обслуживания - '{serv_his.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при изменении записи обслуживания")
                    await state.set_state()
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_service_history_keyboard()))
                case "update_recovery_from_damages__performer":
                    try:
                        compensation_for_dam = await repo.recovery_from_damages.get_create_update_recovery_from_damages(record_id=data.get('recovery_from_damages_id'),
                            payers_id=data.get('performer_id')
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' изменил запись возмещения ущерба - '{compensation_for_dam.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при изменении записи возмещения ущерба")
                    await state.set_state()
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_recovery_from_damages_keyboard()))
                case "update_compensation_for_damages__performer":
                    try:
                        compensation_for_dam = await repo.compensation_for_damages.get_create_update_compensation_for_damages(record_id=data.get('compensation_for_damages_id'),
                            payers_id=data.get('performer_id')
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' изменил запись восстановление после ущерба - '{compensation_for_dam.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при изменении записи восстановление после ущерба")
                    await state.set_state()
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_compensation_for_damages_keyboard()))
                case "update_other_expenses__performer":
                    try:
                        other_expen = await repo.other_expenses.get_create_update_other_expenses(record_id=data.get('other_expenses_id'),
                            performer_id=data.get('performer_id')
                        )
                        logger.info(f"Пользователь '{query.message.chat.id}' изменил запись прочих расходов - '{other_expen.record_id}'")
                    except:
                        logger.info(f"Пользователь '{query.message.chat.id}' ошибка при изменении записи прочих расходов")
                    await state.set_state()
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_other_expenses_keyboard()))
        case "remove":
            match menu:
                case "update_recovery_from_damages__performer" | "update_compensation_for_damages__performer":
                    logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления плательщика - '{menu}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить плательщика?", reply_markup=confirmation_keyboard(action="remove_performer")))
                case _:
                    logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления исполнителя - '{menu}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить исполнителя?", reply_markup=confirmation_keyboard(action="remove_performer")))
        case _:
            pass
"--------------------------------------------"

"------------------SERVICE HISTORY----------------------"
@user_router.callback_query(ServiceHistoryCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: ServiceHistoryCallbackData, bot_custom, repo):
    action = callback_data.action
    match action:
        case "media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню service_history - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(menu="service_history_media",back_menu="service_history")))
        case "change":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню service_history - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_service_history_keyboard()))
        case "remove":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню service_history - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить запись?", reply_markup=confirmation_keyboard(action="remove_service_history")))
        case _:
            pass
"--------------------------------------------"

"------------------COMPENSATION FOR DAMAGES----------------------"
@user_router.callback_query(CompensationForDamagesCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: CompensationForDamagesCallbackData, bot_custom, repo):
    action = callback_data.action
    match action:
        case "media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню compensation_for_damages - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(menu="compensation_for_damages_media",back_menu="compensation_for_damages")))
        case "change":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню compensation_for_damages - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_compensation_for_damages_keyboard()))
        case "remove":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню compensation_for_damages - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить запись?", reply_markup=confirmation_keyboard(action="remove_compensation_for_damages")))
        case _:
            pass
"--------------------------------------------"

"------------------RECOVERY FOR DAMAGES----------------------"
@user_router.callback_query(RecoveryFromDamagesCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: RecoveryFromDamagesCallbackData, bot_custom, repo):
    action = callback_data.action
    match action:
        case "media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню recovery_from_damages - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(menu="recovery_from_damages_media",back_menu="recovery_from_damages")))
        case "change":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню recovery_from_damages - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_recovery_from_damages_keyboard()))
        case "remove":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню recovery_from_damages - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить запись?", reply_markup=confirmation_keyboard(action="remove_recovery_from_damages")))
        case _:
            pass
"--------------------------------------------"

"------------------OTHER EXPENSES----------------------"
@user_router.callback_query(OtherExpensesCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: OtherExpensesCallbackData, bot_custom, repo):
    action = callback_data.action
    match action:
        case "media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню other_expenses - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(menu="other_expenses_media",back_menu="other_expenses")))
        case "change":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню other_expenses - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_other_expenses_keyboard()))
        case "remove":

            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню other_expenses - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить запись?", reply_markup=confirmation_keyboard(action="remove_other_expenses")))
        case _:
            pass
"--------------------------------------------"

"------------------RENT PAYMENT----------------------"
@user_router.callback_query(RentPaymentCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: RentPaymentCallbackData, bot_custom, repo):
    action = callback_data.action
    match action:
        case "change":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню rent_payment - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Что хотите изменить?", reply_markup=update_rent_payment_keyboard()))
        case "remove":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню rent_payment - '{action}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Вы действительно хотите удалить запись?", reply_markup=confirmation_keyboard(action="remove_rent_payment")))
        case _:
            pass
"--------------------------------------------"


"------------------TAXI COMPANY----------------------"
@user_router.callback_query(TaxiCompanyCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: TaxiCompanyCallbackData, bot_custom, repo):
    taxi_company_menu = callback_data.taxi_company_menu
    match taxi_company_menu:
        case "management":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал taxi_company меню - '{taxi_company_menu}'")
            return await management_list(query, bot_custom, repo)
        case "profitability":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню rent_payment - '{taxi_company_menu}'")
            await state.update_data(car_id = None)
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=profit_range_keyboard(menu="taxi_company")))
        case "translations":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню rent_payment - '{taxi_company_menu}'")
            return await all_transfers(query,bot_custom,repo,"taxi_company")
        case _:
            pass
"--------------------------------------------"

"------------------MANAGEMENT----------------------"
@user_router.callback_query(ManagementCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: ManagementCallbackData, bot_custom, repo):
    management_menu = callback_data.management_menu
    driver_id = callback_data.driver_id
    await state.update_data(driver_id=callback_data.driver_id)
    match management_menu:
        case "driver":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню {management_menu} driver_id -'{driver_id}'")
            driver = await repo.drivers.get_driver(driver_id=driver_id)
            birthday = driver.birthdate
            start_work_date = driver.date_of_start_work
            driver_rent = await repo.taxi_company.get_driver_rent_where_driver_id(driver_id=driver_id)
            if driver.photo:
                photo_path = os.path.join(PHOTOS_DIR, "driver", str(driver.driver_id), "facial_photo", f"{driver.photo}.jpg")
                photo = FSInputFile(photo_path)
                bot_custom.messages[query.message.chat.id].append(await query.message.answer_photo(photo=photo, caption=f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}\n\nАрендная плата: {driver_rent}"))
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Изменить:", reply_markup=driver_in_management_keyboard(key="management")))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer(f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}\n\nАрендная плата: {driver_rent}"))
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Изменить:", reply_markup=driver_in_management_keyboard(key="management")))
        case "remove":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню {management_menu} driver_id -'{driver_id}'")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("🔔 Напоминание: При удалении связки нужно уволить водителя в меню водителя,либо создать другую связку с данным водителем.\nВы действительно хотите удалить связку?", reply_markup=confirmation_keyboard(action="remove_management")))
        case _:
            pass
"--------------------------------------------"


"------------------DRIVER IN MANAGEMENT----------------------"
@user_router.callback_query(DriverInManagementCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: DriverInManagementCallbackData, bot_custom, repo):
    driver_in_management_menu = callback_data.driver_in_management_menu
    data = await state.get_data()
    match driver_in_management_menu:
        case "rent_payment":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню {driver_in_management_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer('Введите размер арендной платы'))
            return await state.set_state(UpdateDriverInManagement.DriverRent)
        case "weekends":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню {driver_in_management_menu}")
            weekends = await repo.weekends.get_all_weekends_where_driver_id(driver_id=data.get("driver_id"))
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите выходные дни',reply_markup=weekends_keyboard(weekends=weekends,key="driver_in_management")))
        case _:
            pass
"--------------------------------------------"

"------------------WEEKENDS----------------------"
@user_router.callback_query(WeekendsCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext, callback_data: WeekendsCallbackData, bot_custom, repo):
    weekday = callback_data.weekday
    condition = callback_data.condition
    data = await state.get_data()
    driver_id = data.get("driver_id")
    match condition:
        case "on":
            await repo.weekends.delete_weekend(driver_id=driver_id,week_day=weekday)
            weekends = await repo.weekends.get_all_weekends_where_driver_id(driver_id=driver_id)
            logger.info(f"Пользователь '{query.message.chat.id}' убрал  выходной {weekday} для водителя {driver_id}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите выходные дни', reply_markup=weekends_keyboard(weekends=weekends, key="driver_in_management")))
        case "off":
            await repo.weekends.get_create_update_weekend(driver_id=driver_id,week_day=weekday)
            weekends = await repo.weekends.get_all_weekends_where_driver_id(driver_id=driver_id)
            logger.info(f"Пользователь '{query.message.chat.id}' добавил  выходной {weekday} для водителя {driver_id}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите выходные дни', reply_markup=weekends_keyboard(weekends=weekends, key="driver_in_management")))
        case _:
            pass
"--------------------------------------------"



"------------------UPDATE CAR----------------------"
@user_router.callback_query(UpdateCarCallbackData.filter())
async def answer_qa(query: CallbackQuery,callback_data: UpdateCarCallbackData,bot_custom,state):
    change_menu = callback_data.change_menu
    match change_menu:
        case "facial_photo":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления автомобиля {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте новое лицевое фото"))
            return await state.set_state(UpdateCar.FacialPhoto)
        case "brand":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления автомобиля {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите марку автомобиля"))
            return await state.set_state(UpdateCar.Brand)
        case "model":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления автомобиля {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите модель автомобиля"))
            return await state.set_state(UpdateCar.Model)
        case "release_year":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления автомобиля {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите год выпуска автомобиля"))
            return await state.set_state(UpdateCar.ReleaseYear)
        case "state_number":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления автомобиля {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите гос номер автомобиля"))
            return await state.set_state(UpdateCar.StateNumber)
        case "cost":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления автомобиля {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите стоимость автомобиля"))
            return await state.set_state(UpdateCar.Cost)

        case _:
            pass

@user_router.message(UpdateCar.FacialPhoto)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    if message.video:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Вы отправили видео!Нужно отправить фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Вы отправили видео!\nНужно отправить фото!"))
    elif album:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте одно фото!")
        await album[0].delete()
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте одно фото!"))
    elif message.text or (not message.photo):
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте фото!"))
    else:
        data = await state.get_data()
        car_id = data.get("car_id")
        car_dir = os.path.join(PHOTOS_DIR, "car", str(car_id), "facial_photo")
        os.makedirs(car_dir, exist_ok=True)
        if os.listdir(car_dir):
            for file in os.listdir(car_dir):
                file_split = file.split(".")
                if not file_split[0].endswith("_archive"):
                    # Добавление окончания archive к файлу
                    new_file = file_split[0] + "_archive." + file_split[1]
                    # Переименование файла
                    os.rename(os.path.join(car_dir, file), os.path.join(car_dir, new_file))
        try:
            photos = message.photo
            photo = photos[-1]
            file_id = photo.file_id
            await repo.cars.get_create_update_car(car_id=car_id,
                photo=file_id,
            )
            media_path = os.path.join(car_dir, f'{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            logger.info(f"Пользователь '{message.chat.id}' фото к автомобилю '{car_id}' успешно добавлено!")
            bot_custom.messages[message.chat.id].append(message := await message.answer("Изменение прошло успешно!"))
        except:
            logger.error(f"Пользователь '{message.chat.id}' Произошла ошибка при добавлении фото к автомобилю '{car_id}'!")
            bot_custom.messages[message.chat.id].append(message := await message.answer("Произошла Ошибка!"))
        await asyncio.sleep(2)
    await state.set_state()
    await message.edit_text("Что хотите изменить?")
    return await message.edit_reply_markup(reply_markup=update_car_keyboard())

@user_router.message(UpdateCar.Brand)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    brand = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{brand}' Вы ввели команду!Пожалуйста введите марку автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите марку автомобиля!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{brand}' Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.cars.get_create_update_car(car_id=data.get('car_id'),
        brand=brand,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел марку автомобиля - '{brand}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_car_keyboard()))

@user_router.message(UpdateCar.Model)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    model = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{model}' Вы ввели команду!Пожалуйста введите модель автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите модель автомобиля!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{model}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.cars.get_create_update_car(car_id=data.get('car_id'),
        model=model,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел модель автомобиля - '{model}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_car_keyboard()))

@user_router.message(UpdateCar.ReleaseYear)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        release_year = int(message.text)
    except:
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{release_year}' Вы ввели команду!Пожалуйста введите год выпуска автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите год выпуска автомобиля!"))
    elif len(message.text) > 4:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.cars.get_create_update_car(car_id=data.get('car_id'),
        release_year=release_year,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел год выпуска автомобиля - '{release_year}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_car_keyboard()))

@user_router.message(UpdateCar.StateNumber)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    state_number = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{state_number}' Вы ввели команду!Пожалуйста введите гос номер автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите гос номер автомобиля!"))
    elif len(message.text) > 15:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.cars.get_create_update_car(car_id=data.get('car_id'),
        state_number=state_number,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел гос номер автомобиля - '{state_number}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_car_keyboard()))

@user_router.message(UpdateCar.Cost)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    try:
        cost = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{cost}' Вы ввели команду!Пожалуйста введите стоимость автомобиля!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость автомобиля!"))
    data = await state.get_data()
    await repo.cars.get_create_update_car(car_id=data.get('car_id'),
        cost=cost,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость автомобиля - '{cost}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_car_keyboard()))

"--------------------------------------------"



"------------------UPDATE DRIVER----------------------"
@user_router.callback_query(UpdateDriverCallbackData.filter())
async def answer_qa(query: CallbackQuery,callback_data: UpdateDriverCallbackData,bot_custom,state):
    change_menu = callback_data.change_menu
    match change_menu:
        case "facial_photo":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте лицевое фото"))
            return await state.set_state(UpdateDriver.FacialPhoto)
        case "surname":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите фамилию"))
            return await state.set_state(UpdateDriver.Surname)
        case "name":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите имя"))
            return await state.set_state(UpdateDriver.Name)
        case "patronymic":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите отчество"))
            return await state.set_state(UpdateDriver.Patronymic)
        case "birthdate":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату рождения", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(UpdateDriver.Birthdate)
        case "start_work_date":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату начала работы", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(UpdateDriver.DateOfStartWork)
        case "contact_information":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите контактную информацию"))
            return await state.set_state(UpdateDriver.ContactInformation)
        case "additional_information":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления водителя {change_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите дополнительную информацию"))
            return await state.set_state(UpdateDriver.AdditionalInformation)
        case _:
            pass

@user_router.message(UpdateDriver.FacialPhoto)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo,album: list = None):
    if message.video:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Вы отправили видео!Нужно отправить фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Вы отправили видео!\nНужно отправить фото!"))
    elif album:
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте одно фото!")
        await album[0].delete()
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте одно фото!"))
    elif message.text or (not message.photo):
        logger.error(f"Пользователь '{message.chat.id}' Ошибка! Отправьте фото!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка! Отправьте фото!"))
    else:
        data = await state.get_data()
        driver_id = data.get("driver_id")
        driver_dir = os.path.join(PHOTOS_DIR, "driver", str(driver_id), "facial_photo")
        os.makedirs(driver_dir, exist_ok=True)
        if os.listdir(driver_dir):
            for file in os.listdir(driver_dir):
                file_split = file.split(".")
                if not file_split[0].endswith("_archive"):
                    # Добавление окончания archive к файлу
                    new_file = file_split[0] + "_archive." + file_split[1]
                    # Переименование файла
                    os.rename(os.path.join(driver_dir, file), os.path.join(driver_dir, new_file))
        try:
            photos = message.photo
            photo = photos[-1]
            file_id = photo.file_id
            await repo.drivers.get_create_update_driver(driver_id=driver_id,
                photo=file_id,
            )
            media_path = os.path.join(driver_dir, f'{file_id}.jpg')
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            await message.bot.download_file(file_path, media_path)
            logger.info(f"Пользователь '{message.chat.id}' фото к водителю '{driver_id}' успешно добавлено!")
            bot_custom.messages[message.chat.id].append(message := await message.answer("Изменение прошло успешно!"))
        except:
            logger.error(f"Пользователь '{message.chat.id}' Произошла ошибка при добавлении фото к водителю '{driver_id}'!")
            bot_custom.messages[message.chat.id].append(message := await message.answer("Произошла Ошибка!"))
        await asyncio.sleep(2)
    await state.set_state()
    await message.edit_text("Что хотите изменить?")
    return await message.edit_reply_markup(reply_markup=update_driver_keyboard())

@user_router.message(UpdateDriver.Surname)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    surname = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{surname}' Вы ввели команду!\nПожалуйста введите фамилию!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите фамилию!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{surname}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.drivers.get_create_update_driver(driver_id=data.get('driver_id'),
        surname=surname,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел фамилию водителя - '{surname}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_driver_keyboard()))

@user_router.message(UpdateDriver.Name)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    name = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{name}' Вы ввели команду!Пожалуйста введите имя!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите имя!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{name}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.drivers.get_create_update_driver(driver_id=data.get('driver_id'),
        name=name,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел имя водителя - '{name}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_driver_keyboard()))

@user_router.message(UpdateDriver.Patronymic)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    patronymic = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{patronymic}' Вы ввели команду!Пожалуйста введите отчество!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите отчество!"))
    elif len(message.text) > 128:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{patronymic}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.drivers.get_create_update_driver(driver_id=data.get('driver_id'),
        patronymic=patronymic,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел отчество водителя - '{patronymic}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_driver_keyboard()))


@user_router.message(UpdateDriver.ContactInformation)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    contact_information = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{contact_information}' Вы ввели команду!Пожалуйста введите контактную информацию!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите контактную информацию!"))
    elif len(message.text) > 100:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{contact_information}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.drivers.get_create_update_driver(driver_id=data.get('driver_id'),
        contact_information=contact_information,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел контактную информацию водителя - '{contact_information}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_driver_keyboard()))

@user_router.message(UpdateDriver.AdditionalInformation)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    additional_information = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{additional_information}' Вы ввели команду!Пожалуйста введите дополнительную информацию!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите дополнительную информацию!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{additional_information}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.drivers.get_create_update_driver(driver_id=data.get('driver_id'),
        additional_information=additional_information,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел дополнительную информацию водителя - '{additional_information}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_driver_keyboard()))
"--------------------------------------------"


"------------------UPDATE SERVICE HISTORY----------------------"
@user_router.callback_query(UpdateServiceHistoryCallbackData.filter())
async def answer_qa(query: CallbackQuery,callback_data: UpdateServiceHistoryCallbackData,bot_custom,state,repo):
    action = callback_data.action
    match action:
        case "date":
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(UpdateServiceHistory.Date)
        case "service_type":
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите тип обслуживания"))
            return await state.set_state(UpdateServiceHistory.ServiceType)
        case "amount":
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите стоимость обслуживания"))
            return await state.set_state(UpdateServiceHistory.Amount)
        case "performer":
            menu = "update_service_history__performer"
            await state.update_data(performer_menu=menu)
            await state.set_state(UpdateServiceHistory.PerformerId)
            return await performer_list(query, bot_custom, repo, menu=menu)
        case _:
            pass

@user_router.message(UpdateServiceHistory.ServiceType)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    service_type = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{service_type}' Вы ввели команду!Пожалуйста введите тип обслуживания!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите тип обслуживания!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{service_type}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))

    data = await state.get_data()
    await repo.service_history.get_create_update_service_history(record_id=data.get('service_history_id'),
        service_type=service_type,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел тип обслуживания - '{service_type}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_service_history_keyboard()))

@user_router.message(UpdateServiceHistory.Amount)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость обслуживания!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость обслуживания!"))
    data = await state.get_data()
    await repo.service_history.get_create_update_service_history(record_id=data.get('service_history_id'),
        amount=amount,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел описание - '{amount}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_service_history_keyboard()))
"--------------------------------------------"

"------------------UPDATE COMPENSATION FOR DAMAGES----------------------"
@user_router.callback_query(UpdateCompensationForDamagesCallbackData.filter())
async def answer_qa(query: CallbackQuery,callback_data: UpdateCompensationForDamagesCallbackData,bot_custom,state,repo):
    action = callback_data.action
    match action:
        case "date":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления ущерба {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(UpdateCompensationForDamages.Date)
        case "description":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления ущерба {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите описание"))
            return await state.set_state(UpdateCompensationForDamages.Description)
        case "amount":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления ущерба {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите стоимость обслуживания"))
            return await state.set_state(UpdateCompensationForDamages.Amount)
        case "payers":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления ущерба {action}")
            menu = "update_compensation_for_damages__performer"
            await state.update_data(performer_menu=menu)
            await state.set_state(UpdateCompensationForDamages.PayersId)
            return await performer_list(query, bot_custom, repo, menu=menu)
        case _:
            pass

@user_router.message(UpdateCompensationForDamages.Description)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    description = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Вы ввели команду!Пожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите описание!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))

    data = await state.get_data()
    await repo.compensation_for_damages.get_create_update_compensation_for_damages(record_id=data.get('compensation_for_damages_id'),
        description=description,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел описание - '{description}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_compensation_for_damages_keyboard()))

@user_router.message(UpdateCompensationForDamages.Amount)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость возмещения!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость возмещения!"))
    data = await state.get_data()
    await repo.compensation_for_damages.get_create_update_compensation_for_damages(record_id=data.get('compensation_for_damages_id'),
        amount=amount,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел число - '{amount}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_compensation_for_damages_keyboard()))
"--------------------------------------------"

"------------------UPDATE RENT PAYMENT----------------------"
@user_router.callback_query(UpdateRentPaymentCallbackData.filter())
async def answer_qa(query: CallbackQuery,callback_data: UpdateRentPaymentCallbackData,bot_custom,state,repo):
    action = callback_data.action
    match action:
        case "date_of_payment":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления оплаты аренды {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(UpdateRentPayment.Date)
        case "comment":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления оплаты аренды {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите комментарий"))
            return await state.set_state(UpdateRentPayment.Comment)
        case "amount":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления оплаты аренды {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите сумму"))
            return await state.set_state(UpdateRentPayment.Amount)
        case _:
            pass

@user_router.message(UpdateRentPayment.Comment)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    comment = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{comment}' Вы ввели команду!Пожалуйста введите комментарий!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите комментарий!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{comment}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.rent_payment.get_create_update_rent_payment(payment_id=data.get('payment_id'),comment=comment)
    logger.info(f"Пользователь '{message.chat.id}' ввел комментарий - '{comment}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_rent_payment_keyboard()))

@user_router.message(UpdateRentPayment.Amount)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость возмещения!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость возмещения!"))
    data = await state.get_data()
    await repo.rent_payment.get_create_update_rent_payment(payment_id=data.get('payment_id'), amount=amount)
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость возмещения - '{amount}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_rent_payment_keyboard()))
"--------------------------------------------"


"------------------UPDATE RECOVERY FROM DAMAGES----------------------"
@user_router.callback_query(UpdateRecoveryFromDamagesCallbackData.filter())
async def answer_qa(query: CallbackQuery,callback_data: UpdateRecoveryFromDamagesCallbackData,bot_custom,state,repo):
    action = callback_data.action
    match action:
        case "date":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления после ущерба {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(UpdateRecoveryFromDamages.Date)
        case "description":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления после ущерба {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите описание"))
            return await state.set_state(UpdateRecoveryFromDamages.Description)
        case "amount":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления после ущерба {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите стоимость восстановления"))
            return await state.set_state(UpdateRecoveryFromDamages.Amount)
        case "payers":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления восстановления после ущерба {action}")
            menu = "update_recovery_from_damages__performer"
            await state.update_data(performer_menu=menu)
            await state.set_state(UpdateRecoveryFromDamages.PayersId)
            return await performer_list(query, bot_custom, repo, menu=menu)
        case _:
            pass

@user_router.message(UpdateRecoveryFromDamages.Description)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    description = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Вы ввели команду!Пожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите описание!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))

    data = await state.get_data()
    await repo.recovery_from_damages.get_create_update_recovery_from_damages(record_id=data.get('recovery_from_damages_id'),
        description=description,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел описание- '{description}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_recovery_from_damages_keyboard()))

@user_router.message(UpdateRecoveryFromDamages.Amount)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.tex}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость возмещения!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость возмещения!"))
    data = await state.get_data()
    await repo.recovery_from_damages.get_create_update_recovery_from_damages(record_id=data.get('recovery_from_damages_id'),
        amount=amount,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость возмещения - '{amount}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_recovery_from_damages_keyboard()))
"--------------------------------------------"

"------------------UPDATE OTHER EXPENSES----------------------"
@user_router.callback_query(UpdateOtherExpensesCallbackData.filter())
async def answer_qa(query: CallbackQuery,callback_data: UpdateOtherExpensesCallbackData,bot_custom,state,repo):
    action = callback_data.action
    match action:
        case "date":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления прочих расходов {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(UpdateOtherExpenses.Date)
        case "description":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления прочих расходов {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите описание"))
            return await state.set_state(UpdateOtherExpenses.Description)
        case "amount":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления прочих расходов {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите стоимость расхдов"))
            return await state.set_state(UpdateOtherExpenses.Amount)
        case "performer":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню обновления прочих расходов {action}")
            menu = "update_other_expenses__performer"
            await state.update_data(performer_menu=menu)
            await state.set_state(UpdateOtherExpenses.PayersId)
            return await performer_list(query, bot_custom, repo, menu=menu)
        case _:
            pass

@user_router.message(UpdateOtherExpenses.Description)
async def answer_qa(message: Message,state: FSMContext,bot_custom,repo):
    description = message.text
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Вы ввели команду!Пожалуйста введите описание!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите описание!"))
    elif len(message.text) > 255:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{description}' Превышено допустимое количество сиволов!Пожалуйста повторите ввод!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Превышено допустимое количество сиволов!\nПожалуйста повторите ввод!"))
    data = await state.get_data()
    await repo.other_expenses.get_create_update_other_expenses(record_id=data.get('other_expenses_id'),
        description=description,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел описание - '{description}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_other_expenses_keyboard()))

@user_router.message(UpdateOtherExpenses.Amount)
async def answer_qa(message: Message, state: FSMContext, bot_custom, repo):
    try:
        amount = float(message.text)
    except:
        logger.error(f"Пользователь '{message.chat.id}' ввел '{message.text}' Ошибка!Пожалуйста введите число!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Ошибка!\nПожалуйста введите число!"))
    if message.text.startswith("/"):
        logger.error(f"Пользователь '{message.chat.id}' ввел '{amount}' Вы ввели команду!Пожалуйста введите стоимость возмещения!")
        return bot_custom.messages[message.chat.id].append(await message.answer("Вы ввели команду!\nПожалуйста введите стоимость возмещения!"))
    data = await state.get_data()
    await repo.other_expenses.get_create_update_other_expenses(record_id=data.get('other_expenses_id'),
        amount=amount,
    )
    logger.info(f"Пользователь '{message.chat.id}' ввел стоимость возмещения - '{amount}'")
    return bot_custom.messages[message.chat.id].append(await message.answer("Что хотите изменить?", reply_markup=update_other_expenses_keyboard()))
"--------------------------------------------"

"------------------CONFIRMATION----------------------"
@user_router.callback_query(ConfirmationCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext,callback_data: ConfirmationCallbackData,bot_custom,repo):
    action = callback_data.action
    answer = callback_data.answer
    data = await state.get_data()
    match action:
        case "remove_car":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            car_id = data.get("car_id")
            match answer:
                case "yes":
                    try:
                        taxi_driver_exemp = await repo.taxi_company.get_taxi_company_where_car_id(car_id=car_id)
                        if taxi_driver_exemp:
                            logger.info(f"Пользователь '{query.message.chat.id}' Внимание‼ К данному автомобилю прикреплен водитель.При удалениии автомобилю связь с водителем будет разорвана‼Продолжить удаление?️")
                            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Внимание‼ К данному автомобилю прикреплен водитель.\nПри удалениии автомобилю связь с водителем будет разорвана‼\nПродолжить удаление?️", reply_markup=confirmation_keyboard(action="remove_car_in_taxi_company")))
                    except:
                        pass
                    await repo.cars.delete_car(car_id= car_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил атвомобиль - '{car_id}'")
                    return await car_list(query, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление автомобиля - '{car_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с автомобилем', reply_markup=car_keyboard()))
        case "remove_car_in_taxi_company":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            car_id = data.get("car_id")
            match answer:
                case "yes":
                    await repo.taxi_company.remove_taxi_company(car_id=car_id)
                    await repo.cars.delete_car(car_id= car_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил связку с автоиобилем- '{car_id}'")
                    return await car_list(query, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление связки с автоиобилем- '{car_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с автомобилем', reply_markup=car_keyboard()))
        case "dismiss_driver":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            driver_id = data.get("driver_id")
            match answer:
                case "yes":
                    try:
                        taxi_driver_exemp = await repo.taxi_company.get_object_where_driver_id(driver_id=driver_id)
                        if taxi_driver_exemp:
                            logger.info(f"Пользователь '{query.message.chat.id}' Внимание‼ К данному водителю прикреплен автомобиль.При удалениии водителя связь с автомобилем будет разорвана‼Продолжить увольнение?️")
                            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Внимание‼ К данному водителю прикреплен автомобиль.\nПри удалениии водителя связь с автомобилем будет разорвана‼\nПродолжить увольнение?️", reply_markup=confirmation_keyboard(action="dismiss_driver_car_in_taxi_company")))
                    except:
                        pass
                    await repo.drivers.delete_driver(driver_id=driver_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил водителя- '{driver_id}'")
                    return await driver_list(query, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие водителя- '{driver_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с водителем', reply_markup=driver_keyboard()))
        case "dismiss_driver_car_in_taxi_company":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            driver_id = data.get("driver_id")
            match answer:
                case "yes":
                    await repo.taxi_company.remove_taxi_company(driver_id=driver_id)
                    await repo.drivers.delete_driver(driver_id=driver_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил связку и водителя где водитель - '{driver_id}'")
                    return await driver_list(query, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие связки и водителя где автомобиль - '{driver_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с водителем', reply_markup=driver_keyboard()))
        case "remove_performer":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            car_id = data.get("car_id")
            match answer:
                case "yes":
                    await repo.performers.remove_performer(performer_id=data.get("performer_id"))
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил исполнителя - '{car_id}'")
                    return await performer_list(query, bot_custom, repo, menu=data.get("performer_menu"))
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие исполнителя - '{car_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с исполнителем', reply_markup=performer_keyboard(data.get("performer_menu"))))
        case "remove_management":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            driver_id = data.get("driver_id")
            match answer:
                case "yes":
                    await repo.taxi_company.remove_taxi_company(driver_id=driver_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил связку где водитель - '{driver_id}'")
                    return await management_list(query, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие связки где автомобиль - '{driver_id}'")
                    return await management_list(query, bot_custom, repo)
        case "remove_service_history":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            service_history_id = data.get("service_history_id")
            match answer:
                case "yes":
                    await repo.service_history.remove_service_history(record_id=service_history_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил запись обслуживания - '{service_history_id}'")
                    return await service_history_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие запись обслуживания - '{service_history_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=service_history_keyboard()))
        case "remove_compensation_for_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            compensation_for_damages_id = data.get("compensation_for_damages_id")
            match answer:
                case "yes":
                    await repo.compensation_for_damages.remove_compensations_for_damages(record_id=compensation_for_damages_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил запись восстановления после ущерба - '{compensation_for_damages_id}'")
                    return await compensation_for_damages_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие запись восстановления после ущерба - '{compensation_for_damages_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=compensation_for_damages_keyboard()))
        case "remove_recovery_from_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            recovery_from_damages_id = data.get("recovery_from_damages_id")
            match answer:
                case "yes":
                    await repo.recovery_from_damages.remove_recovery_from_damages(record_id=recovery_from_damages_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил запсь восстановления после ущерба - '{recovery_from_damages_id}'")
                    return await recovery_from_damages_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие запсь восстановления после ущерба - '{recovery_from_damages_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=recovery_from_damages_keyboard()))
        case "remove_other_expenses":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            other_expenses_id = data.get("other_expenses_id")
            match answer:
                case "yes":
                    await repo.other_expenses.remove_other_expenses(record_id=other_expenses_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил заапись прочих расходов - '{other_expenses_id}'")
                    return await other_expenses_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие заапись прочих расходов - '{other_expenses_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=other_expenses_keyboard()))
        case "remove_rent_payment":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            payment_id = data.get("payment_id")
            match answer:
                case "yes":
                    await repo.rent_payment.remove_rent_payment(payment_id=payment_id)
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил перевод - '{payment_id}'")
                    return await rent_payment_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удалениие перевода - '{payment_id}'")
                    return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=rent_payment_keyboard()))
        case "remove_inspection":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            record_id = data.get("remove_record_id")
            car_id = data.get("car_id")
            match answer:
                case "yes":
                    media_path = data.get("media_path")
                    media_path = media_path[str(record_id)]
                    media_path_split = media_path.split(".")
                    expansion = media_path_split[1]
                    new_dir_path = media_path_split[0] + "_archive_1"
                    # Переименование директории
                    while True:
                        try:
                            os.rename(media_path, new_dir_path + "." + expansion)
                            break
                        except:
                            val = int(new_dir_path[-1]) + 1
                            new_dir_path = new_dir_path[:-1] + f"{val}"
                            continue
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил осмотр'{record_id}' автомобиля {car_id}")
                    return await inspections_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление осмотра '{record_id}' автомобиля {car_id}")
                    return await inspections_list(query, state, bot_custom, repo)
        case "remove_media":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            record_id = data.get("remove_record_id")
            driver_id = data.get("driver_id")
            match answer:
                case "yes":

                    media_path = data.get("media_path")
                    media_path = media_path[str(record_id)]
                    media_path_split = media_path.split(".")
                    expansion = media_path_split[1]
                    new_dir_path = media_path_split[0] + "_archive_1"
                    # Переименование директории
                    while True:
                        try:
                            os.rename(media_path, new_dir_path + "." + expansion)
                            break
                        except:
                            val = int(new_dir_path[-1]) + 1
                            new_dir_path = new_dir_path[:-1] + f"{val}"
                            continue
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил медиа '{record_id}' водителя {driver_id}")
                    return await media_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление медиа '{record_id}' водителя {driver_id}")
                    return await media_list(query, state, bot_custom, repo)
        case "remove_media_compensation_for_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            record_id = data.get("remove_record_id")
            compensation_for_damages_id = data.get("compensation_for_damages_id")
            match answer:
                case "yes":
                    media_path = data.get("media_path")
                    media_path = media_path[str(record_id)]
                    media_path_split = media_path.split(".")
                    expansion = media_path_split[1]
                    new_dir_path = media_path_split[0] + "_archive_1"
                    # Переименование директории
                    while True:
                        try:
                            os.rename(media_path, new_dir_path + "." + expansion)
                            break
                        except:
                            val = int(new_dir_path[-1]) + 1
                            new_dir_path = new_dir_path[:-1] + f"{val}"
                            continue
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил медиа '{record_id}' восстановления ущерба {compensation_for_damages_id}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление медиа '{record_id}' восстановления ущерба {compensation_for_damages_id}")
                    return await expenses_list(query, state, bot_custom, repo)
        case "remove_media_service_history":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            record_id = data.get("remove_record_id")
            service_history_id = data.get("service_history_id")
            match answer:
                case "yes":
                    media_path = data.get("media_path")
                    media_path = media_path[str(record_id)]
                    media_path_split = media_path.split(".")
                    expansion = media_path_split[1]
                    new_dir_path = media_path_split[0] + "_archive_1"
                    # Переименование директории
                    while True:
                        try:
                            os.rename(media_path, new_dir_path + "." + expansion)
                            break
                        except:
                            val = int(new_dir_path[-1]) + 1
                            new_dir_path = new_dir_path[:-1] + f"{val}"
                            continue
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил медиа '{record_id}' обслуживания {service_history_id}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление медиа '{record_id}' обслуживания {service_history_id}")
                    return await expenses_list(query, state, bot_custom, repo)
        case "remove_media_recovery_from_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            record_id = data.get("remove_record_id")
            recovery_from_damages_id = data.get("recovery_from_damages_id")
            match answer:
                case "yes":
                    media_path = data.get("media_path")
                    media_path = media_path[str(record_id)]
                    media_path_split = media_path.split(".")
                    expansion = media_path_split[1]
                    new_dir_path = media_path_split[0] + "_archive_1"
                    # Переименование директории
                    while True:
                        try:
                            os.rename(media_path, new_dir_path + "." + expansion)
                            break
                        except:
                            val = int(new_dir_path[-1]) + 1
                            new_dir_path = new_dir_path[:-1] + f"{val}"
                            continue
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил медиа '{record_id}' восстановления после ущерба {recovery_from_damages_id}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление медиа '{record_id}' восстановления после ущерба {recovery_from_damages_id}")
                    return await expenses_list(query, state, bot_custom, repo)
        case "remove_media_other_expenses":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            record_id = data.get("remove_record_id")
            other_expenses_id = data.get("other_expenses_id")
            match answer:
                case "yes":
                    media_path = data.get("media_path")
                    media_path = media_path[str(record_id)]
                    media_path_split = media_path.split(".")
                    expansion = media_path_split[1]
                    new_dir_path = media_path_split[0] + "_archive_1"
                    # Переименование директории
                    while True:
                        try:
                            os.rename(media_path, new_dir_path + "." + expansion)
                            break
                        except:
                            val = int(new_dir_path[-1]) + 1
                            new_dir_path = new_dir_path[:-1] + f"{val}"
                            continue
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил медиа '{record_id}' прочих расходов {other_expenses_id}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление медиа '{record_id}' прочих расходов {other_expenses_id}")
                    return await expenses_list(query, state, bot_custom, repo)
        case "add_car_facial_photo":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            car_id = data.get("car_id")
            match answer:
                case "yes":
                    bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте лицевое фото"))
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил лицевое фото автомобиля {car_id}")
                    return await state.set_state(AddCar.FacialPhoto)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление лицевого фото автомобиля {car_id}")
                    return await car_list(query, bot_custom, repo)
        case "add_driver_facial_photo":
            logger.info(f"Пользователь '{query.message.chat.id}' выбрал меню удаления - '{action}'")
            driver_id = data.get("driver_id")
            match answer:
                case "yes":
                    bot_custom.messages[query.message.chat.id].append(await query.message.answer("Отправьте лицевое фото"))
                    logger.info(f"Пользователь '{query.message.chat.id}' удалил лицевое фото водителя {driver_id}")
                    return await state.set_state(AddDriver.FacialPhoto)
                case "no":
                    logger.info(f"Пользователь '{query.message.chat.id}' отменил удаление лицевого фото водителя {driver_id}")
                    return await driver_list(query, bot_custom, repo)
        case _:
            pass
"--------------------------------------------"

"------------------RANGE----------------------"
@user_router.callback_query(RangeCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext,callback_data: RangeCallbackData,bot_custom,repo):
    action = callback_data.action
    menu = callback_data.menu
    await state.update_data(menu=menu)
    match action:
        case "week":
            await state.update_data(range="week")
            match menu:
                case "translations":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await rent_payment_list(query, state, bot_custom, repo)
                case "inspections":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await inspections_list(query, state,bot_custom, repo)
                case "media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await media_list(query, state, bot_custom, repo)
                case "service_history_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "compensation_for_damages_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "recovery_from_damages_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "other_expenses_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
        case "month":
            await state.update_data(range="month")
            match menu:
                case "translations":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await rent_payment_list(query, state, bot_custom, repo)
                case "inspections":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await inspections_list(query, state,bot_custom, repo)
                case "media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await media_list(query, state, bot_custom, repo)
                case "service_history_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "compensation_for_damages_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "recovery_from_damages_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "other_expenses_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
        case "all_time":
            await state.update_data(range="all_time")
            match menu:
                case "translations":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await rent_payment_list(query, state, bot_custom, repo)
                case "inspections":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await inspections_list(query, state,bot_custom, repo)
                case "media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await media_list(query, state, bot_custom, repo)
                case "service_history_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "compensation_for_damages_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "recovery_from_damages_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
                case "other_expenses_media":
                    logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
                    return await expenses_list(query, state, bot_custom, repo)
        case "range":
            await state.update_data(range="user_range")
            await state.update_data(menu=menu)
            logger.info(f"Пользователь '{query.message.chat.id}' показать {menu} за {action}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату начала диапазона", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(AddRange.StartDate)
        case _:
            pass
"--------------------------------------------"

"------------------PROFIT RANGE----------------------"
@user_router.callback_query(ProfitRangeCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext,callback_data: ProfitRangeCallbackData,bot_custom,repo):
    action = callback_data.action
    data = await state.get_data()
    try:
        car_id = data.get('car_id')
    except:
        car_id = None
    match action:
        case "year":
            logger.info(f"Пользователь '{query.message.chat.id}' показать profit range за {action} где car_id {car_id}")
            today = date.today()
            year_ago = today - timedelta(days=365)
            if car_id:
                return await car_financial_calculation(query, bot_custom, repo, "car", car_id=car_id,user_date=year_ago)
            else:
                return await car_financial_calculation(query, bot_custom, repo, "taxi_company",user_date=year_ago)
        case "all_time":
            logger.info(f"Пользователь '{query.message.chat.id}' показать profit range за {action} где car_id {car_id}")
            if car_id:
                return await car_financial_calculation(query, bot_custom, repo, "car", car_id=car_id)
            else:
                return await car_financial_calculation(query, bot_custom, repo, "taxi_company")
        case "range":
            logger.info(f"Пользователь '{query.message.chat.id}' показать profit range за {action} где car_id {car_id}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Выберите дату начала диапазона", reply_markup=await DialogCalendar().start_calendar()))
            return await state.set_state(AddProfitRange.StartDate)
        case _:
            pass
"--------------------------------------------"


"------------------BACK----------------------"
@user_router.callback_query(BackCallbackData.filter())
async def answer_qa(query: CallbackQuery,state: FSMContext,callback_data: BackCallbackData,bot_custom,repo):
    back_menu = callback_data.back_menu
    data = await state.get_data()
    match back_menu:
        case "car" | "car_menu":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с автомобилем', reply_markup=car_keyboard()))
        case "driver"| "driver_menu":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие с водителем', reply_markup=driver_keyboard()))
        case "taxi_company":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("ТАКСОПАРК 🚖", reply_markup=taxi_company_keyboard()))
        case "car_list":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await car_list(query,bot_custom,repo)
        case "management":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await management_list(query, bot_custom, repo)
        case "driver_list":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await driver_list(query,bot_custom,repo)
        case "performer_list" | "compensation_for_damages__performer" | "service_history__performer"| "recovery_from_damages__performer"|"other_expenses__performer":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            menu = data.get("performer_menu")
            return await performer_list(query, bot_custom, repo,menu = menu)
        case "main":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Привет! Я бот для управления таксопарком.', reply_markup=main_keyboard()))
        case "range":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Показать записи за", reply_markup=range_keyboard(back_menu="driver",menu="translations")))
        case "amount":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            bot_custom.messages[query.message.chat.id].append(await query.message.answer("Введите стоимость возмещения ущерба"))
            return await state.set_state(AddCompensationForDamages.Amount)
        case "driver_in_management":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            driver_id = data.get("driver_id")
            driver = await repo.drivers.get_driver(driver_id=driver_id)
            birthday = driver.birthdate
            start_work_date = driver.date_of_start_work
            driver_rent = await repo.taxi_company.get_driver_rent_where_driver_id(driver_id=driver_id)
            if driver.photo:
                photo_path = os.path.join(PHOTOS_DIR, "driver", str(driver.driver_id), "facial_photo", f"{driver.photo}.jpg")
                photo = FSInputFile(photo_path)
                bot_custom.messages[query.message.chat.id].append(await query.message.answer_photo(photo=photo, caption=f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}\n\nАрендная плата: {driver_rent}"))
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Изменить:", reply_markup=driver_in_management_keyboard(key="management")))
            else:
                bot_custom.messages[query.message.chat.id].append(await query.message.answer(f"Фамилия: {driver.surname}\nИмя: {driver.name}\nОтчество: {driver.patronymic}\nДата рождения: {birthday.strftime('%d.%m.%Y')}\nДата начала работы: {start_work_date.strftime('%d.%m.%Y')}\nКонтактная информация: {driver.contact_information}\nДополнительная информация: {driver.additional_information}\n\nАрендная плата: {driver_rent}"))
                return bot_custom.messages[query.message.chat.id].append(await query.message.answer("Изменить:", reply_markup=driver_in_management_keyboard(key="management")))
        case "service_history":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await service_history_list(query, state, bot_custom, repo)
        case "compensation_for_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await compensation_for_damages_list(query, state, bot_custom, repo)
        case "recovery_from_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await recovery_from_damages_list(query, state, bot_custom, repo)
        case "other_expenses":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await other_expenses_list(query, state, bot_custom, repo)
        case "rent_payment":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return await rent_payment_list(query, state, bot_custom, repo)
        case "update_service_history":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=service_history_keyboard()))
        case "update_compensation_for_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=compensation_for_damages_keyboard()))
        case "update_recovery_from_damages":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=recovery_from_damages_keyboard()))
        case "update_other_expenses":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=other_expenses_keyboard()))
        case "update_rent_payment":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Выберите действие', reply_markup=rent_payment_keyboard()))
        case "update_service_history__performer":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Что хотите изменить?', reply_markup=update_service_history_keyboard()))
        case "update_compensation_for_damages__performer":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Что хотите изменить?', reply_markup=update_compensation_for_damages_keyboard()))
        case "update_recovery_from_damages__performer":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Что хотите изменить?', reply_markup=update_recovery_from_damages_keyboard()))
        case "update_other_expenses__performer":
            logger.info(f"Пользователь '{query.message.chat.id}' вернулся в меню {back_menu}")
            return bot_custom.messages[query.message.chat.id].append(await query.message.answer('Что хотите изменить?', reply_markup=update_other_expenses_keyboard()))
        case _:
                pass
"--------------------------------------------"


"------------------CALENDAR----------------------"
@user_router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(query: CallbackQuery,state: FSMContext, callback_data: dict):
    selected, calendar_date = await SimpleCalendar().process_selection(query, callback_data)
    if selected:
        pass
@user_router.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(query: CallbackQuery, state: FSMContext, callback_data: dict, repo, bot_custom):
    selected, calendar_date = await DialogCalendar().process_selection(query, callback_data)
    state_now = await state.get_state()
    data = await state.get_data()
    if callback_data.act != 'CANCEL':
        if selected:
            date_str = calendar_date.strftime("%Y-%m-%d %H:%M:%S")
            match state_now:
                case "AddDriver:Birthdate":
                    logger.info(f"Пользователь '{query.message.chat.id}' выбрал добавление дня рожденья водителя")
                    await state.update_data(birthdate=date_str)
                    await query.message.edit_text("Выберите дату начала работы")
                    await query.message.edit_reply_markup(reply_markup=await DialogCalendar().start_calendar())
                    return await state.set_state(AddDriver.DateOfStartWork)
                case "AddProfitRange:StartDate":
                    await state.set_state()
                    await query.message.delete()
                    try:
                        car_id = data.get('car_id')
                    except:
                        car_id = None
                    logger.info(f"Пользователь '{query.message.chat.id}' выбрал дату начала диапазона доходности car_id - {car_id}")
                    if car_id:
                        return await car_financial_calculation(query, bot_custom, repo, "car", car_id=car_id,user_date=calendar_date.date())
                    else:
                        return await car_financial_calculation(query, bot_custom, repo, "taxi_company",user_date=calendar_date)
                case "AddRange:StartDate":
                    logger.info(f"Пользователь '{query.message.chat.id}' выбрал дату начала диапазона")
                    await state.update_data(start_date=date_str)
                    await query.message.edit_text("Выберите дату конца диапазона")
                    await query.message.edit_reply_markup(reply_markup=await DialogCalendar().start_calendar())
                    return await state.set_state(AddRange.EndDate)
                case "AddRange:EndDate":
                    logger.info(f"Пользователь '{query.message.chat.id}' выбрал дату конца диапазона menu - {data.get('menu')}")
                    await state.update_data(end_date=date_str)
                    await query.message.delete()
                    await state.set_state()
                    match data.get("menu"):
                        case "translations":
                            return await rent_payment_list(query, state, bot_custom, repo)
                        case "inspections":
                            return await inspections_list(query, state, bot_custom, repo)
                        case "media":
                            return await media_list(query, state, bot_custom, repo)
                        case "service_history_media":
                            return await expenses_list(query, state, bot_custom, repo)
                        case "compensation_for_damages_media":
                            return await expenses_list(query, state, bot_custom, repo)
                        case "recovery_from_damages_media":
                            return await expenses_list(query, state, bot_custom, repo)
                        case "other_expenses_media":
                            return await expenses_list(query, state, bot_custom, repo)
                case "AddDriver:DateOfStartWork":
                    logger.info(f"Пользователь '{query.message.chat.id}' выбрал дату начала работы для водителя")
                    await state.update_data(date_of_start_work=date_str)
                    await query.message.edit_text("Введите контактную информацию")
                    return await state.set_state(AddDriver.ContactInformation)
                case "UpdateDriver:Birthdate":
                    logger.info(f"Пользователь '{query.message.chat.id}' обновил дату рождения водителя")
                    await repo.drivers.get_create_update_driver(driver_id=data.get('driver_id'),
                        birthdate=calendar_date,
                    )
                    await state.set_state()
                    await query.message.edit_text("Что хотите изменить?")
                    return await query.message.edit_reply_markup(reply_markup=update_driver_keyboard())
                case "UpdateDriver:DateOfStartWork":
                    logger.info(f"Пользователь '{query.message.chat.id}' обновил дату начала работы водителя")
                    await repo.drivers.get_create_update_driver(driver_id=data.get('driver_id'),
                        date_of_start_work=calendar_date,
                    )
                    await state.set_state()
                    await query.message.edit_text("Что хотите изменить?")
                    return await query.message.edit_reply_markup(reply_markup=update_driver_keyboard())
                case "AddCompensationForDamages:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' добавил дату для CompensationForDamages")
                    await state.update_data(date=date_str)
                    await query.message.edit_text("Введите описание")
                    return await state.set_state(AddCompensationForDamages.Description)
                case "AddServiceHistory:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' добавил дату для ServiceHistory")
                    await state.update_data(date=date_str)
                    await query.message.edit_text("Введите тип обслуживания")
                    return await state.set_state(AddServiceHistory.ServiceType)
                case "AddRecoveryFromDamages:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' добавил дату для RecoveryFromDamages")
                    await state.update_data(date=date_str)
                    await query.message.edit_text("Введите описание")
                    return await state.set_state(AddRecoveryFromDamages.Description)
                case "AddOtherExpenses:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' добавил дату для OtherExpenses")
                    await state.update_data(date=date_str)
                    await query.message.edit_text("Введите описание")
                    return await state.set_state(AddOtherExpenses.Description)
                case "AddRentPayment:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' добавил дату для RentPayment")
                    await state.update_data(date=date_str)
                    await query.message.edit_text("Введите комментарий")
                    return await state.set_state(AddRentPayment.Сomment)
                case "UpdateRentPayment:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' обновил дату для RentPayment")
                    await repo.rent_payment.get_create_update_rent_payment(payment_id=data.get('payment_id'), date=calendar_date)
                    await state.set_state()
                    await query.message.edit_text("Что хотите изменить?")
                    return await query.message.edit_reply_markup(reply_markup=update_rent_payment_keyboard())
                case "UpdateServiceHistory:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' обновил дату для ServiceHistory")
                    await repo.service_history.get_create_update_service_history(record_id=data.get('service_history_id'),
                        date=calendar_date,
                    )
                    await query.message.edit_text("Что хотите изменить?")
                    return await query.message.edit_reply_markup(reply_markup=update_service_history_keyboard())
                case "UpdateCompensationForDamages:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' обновил дату для CompensationForDamages")
                    await repo.compensation_for_damages.get_create_update_compensation_for_damages(record_id=data.get('compensation_for_damages_id'),
                        date=calendar_date,
                    )
                    await query.message.edit_text("Что хотите изменить?")
                    return await query.message.edit_reply_markup(reply_markup=update_compensation_for_damages_keyboard())
                case "UpdateRecoveryFromDamages:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' обновил дату для RecoveryFromDamages")
                    await repo.recovery_from_damages.get_create_update_recovery_from_damages(record_id=data.get('recovery_from_damages_id'),
                        date=calendar_date,
                    )
                    await query.message.edit_text("Что хотите изменить?")
                    return await query.message.edit_reply_markup(reply_markup=update_recovery_from_damages_keyboard())
                case "UpdateOtherExpenses:Date":
                    logger.info(f"Пользователь '{query.message.chat.id}' обновил дату для OtherExpenses")
                    await repo.other_expenses.get_create_update_other_expenses(record_id=data.get('other_expenses_id'),
                        date=calendar_date,
                    )
                    await query.message.edit_text("Что хотите изменить?")
                    return await query.message.edit_reply_markup(reply_markup=update_other_expenses_keyboard())
    else:
        await query.message.delete()
        await state.clear()
        bot_custom.messages[query.message.chat.id].append(await query.message.answer('Привет! Я бот для управления таксопарком.', reply_markup=main_keyboard()))


"--------------------------------------------"

@user_router.message(F.text,IsPrivate())
async def navigat(message: Message,bot_custom):
    return bot_custom.messages[message.chat.id].append(await message.answer(f"Ошибка! Команда не найдена"))

@user_router.errors()
async def errors_handler(exception):
    if isinstance(exception, TelegramBadRequest):
        pass
    else:
        pass