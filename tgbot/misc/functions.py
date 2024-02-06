import datetime

from aiogram.types import User
from aiogram.utils.markdown import hcode
from sqlalchemy.ext.asyncio import AsyncSession

def get_first_digit(number):
    while number >= 10:
        number //= 10
    return number

def split_list(lst):
    n = 10
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def calculate_return_on_investment(profit, investment_size):
    return round((profit / investment_size) * 100,2)

def convert_days_to_years_months_days(days):
    out = ""
    if count_year := days // 365:
        if count_year % 10 == 1:
            out_text_years = 'год'
        elif 1 < count_year % 10 < 5:
            out_text_years = 'года'
        else:
            out_text_years = 'лет'
        out += f"{count_year} {out_text_years}"
        if count_month := (days - (count_year*365)) // 31:
            if count_month % 10 == 1 and count_month % 100 != 11:
                out_text_month = "месяц"
            elif 2 <= count_month % 10 <= 4 and (count_month % 100 < 10 or count_month % 100 >= 20):
                out_text_month = "месяца"
            else:
                out_text_month = "месяцев"
            out += f" {count_month} {out_text_month}"
            if count_days := (days - (count_year*365) - (count_month*31)):
                if count_days % 10==1 and count_days % 100 != 11:
                    out_text_days = 'день'
                elif 1 < count_days % 10 < 5 and get_first_digit(count_days) != 1:
                    out_text_days = 'дня'
                else:
                    out_text_days = 'дней'
                out += f" {count_days} {out_text_days}"
        return out
    elif count_month := days // 31:
        if count_month % 10 == 1 and count_month % 100 != 11:
            out_text_month = "месяц"
        elif 2 <= count_month % 10 <= 4 and (count_month % 100 < 10 or count_month % 100 >= 20):
            out_text_month = "месяца"
        else:
            out_text_month = "месяцев"
        return f"{count_month} {out_text_month}"
    else:
        if days % 10 == 1 and days % 100 != 11:
            out_text_days = 'день'
        elif 1 < days % 10 < 5 and get_first_digit(days) != 1:
            out_text_days = 'дня'
        else:
            out_text_days = 'дней'
        return f"{days} {out_text_days}"
