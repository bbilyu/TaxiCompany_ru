
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message,TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self,second_of_block: int,second_rate_limit: int | float):
        self.second_of_block = second_of_block
        self.second_rate_limit = second_rate_limit
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = f"user{event.from_user.id}"
        check_user = await data['fsm_storage'].redis.get(name=user)
        if check_user:
            if int(check_user.decode()):
                await data['fsm_storage'].redis.set(name=user,value=0,ex=self.second_of_block)
                # return await event.answer("Обнаружена подазриьельная ативность")
            return event.delete()
        if isinstance(self.second_rate_limit,int):
            await data['fsm_storage'].redis.set(name=user, value=1, ex=self.second_rate_limit)
        elif isinstance(self.second_rate_limit, float):
            if self.second_rate_limit < 1:
                await data['fsm_storage'].redis.set(name=user,value=1,px=int(self.second_rate_limit*1000))
            else:
                await data['fsm_storage'].redis.set(name=user, value=1, ex=int(self.second_rate_limit))
        return await handler(event,data)