from typing import Callable, Dict, Any, Awaitable, Union, List

from aiogram import BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.types import Message, CallbackQuery


class DeleteMessagesMiddleware(BaseMiddleware):
    def __init__(self):
        self._messages = {}
        self._callbacks = {}
        # self._callbacks: Union[List[CallbackQuery]] = []
        self.states_ignore = ["AddDriver:Birthdate","AddDriver:DateOfStartWork","UpdateDriver:Birthdate","UpdateDriver:DateOfStartWork","AddCompensationForDamages:Date","AddServiceHistory:Date","AddRecoveryFromDamages:Date","AddOtherExpenses:Date","AddRange:StartDate","AddRange:EndDate","AddRentPayment:Date","UpdateServiceHistory:Date","UpdateCompensationForDamages:Date","UpdateRecoveryFromDamages:Date","UpdateOtherExpenses:Date","AddProfitRange:StartDate","UpdateRentPayment:Date"]
    @property
    def messages(self) -> List[Message]:
        return self._messages

    @messages.setter
    def messages(self, messages: List[Message]):
        self._messages = messages

    @property
    def callbacks(self) -> List[CallbackQuery]:
        return self._callbacks

    @callbacks.setter
    def callbacks(self, callbacks: List[CallbackQuery]):
        self._callbacks = callbacks
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        data['bot_custom'] = self
        if isinstance(event, Message):
            if (user_id := event.chat.id) not in self._messages:
                self._messages[user_id] = []
            await event.delete()
        elif isinstance(event, CallbackQuery):
            if (user_id := event.message.chat.id) not in self._messages:
                self._messages[user_id] = []
            self._messages[user_id].append(event.message)
        if data['raw_state'] not in self.states_ignore:
            for mess in self._messages[user_id]:
                if mess.chat.id == user_id:
                    try:
                        await mess.delete()
                    except:
                        pass
            self._messages[user_id].clear()
        return await handler(event, data)
