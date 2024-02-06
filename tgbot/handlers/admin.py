from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from tgbot.filters.private_chat import IsPrivate

admin_router = Router()

filters = [IsPrivate()]

for filter in filters:
    admin_router.message.filter(filter)


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.reply("Привет,Админ!")
