from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from tgbot.config import Config


class UserFilter(BaseFilter):
    is_user: bool = True
    async def __call__(self, obj: Message | CallbackQuery, config: Config) -> bool:
        if isinstance(obj, Message):
            return ((obj.from_user.id in config.tg_bot.user_ids) or (obj.from_user.id in config.tg_bot.admin_ids)) == self.is_user
        else:
            return ((obj.message.chat.id in config.tg_bot.user_ids) or (obj.message.chat.id in config.tg_bot.admin_ids))==self.is_user
