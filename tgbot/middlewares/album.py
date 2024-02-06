import asyncio
from typing import Callable, Dict, Any, Awaitable,Union

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlmubMiddleware(BaseMiddleware):
    def __init__(self,latency: Union[int,float] = 0.1):
        self.latency = latency
        self.album_data = {}

    def colelct_album_messages(self, event: Message):

        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = {'messages': []}

        self.album_data[event.media_group_id]['messages'].append(event)

        return len(self.album_data[event.media_group_id]['messages'])

    async def __call__(self, handler,event:Message, data: Dict[str, Any]) -> Any:
        if not event.media_group_id:
            return await handler(event,data)

        total_before = self.colelct_album_messages(event)

        await asyncio.sleep(self.latency)

        total_after = len(self.album_data[event.media_group_id]['messages'])

        if total_after != total_before:
            return
        album_messages = self.album_data[event.media_group_id]["messages"]
        album_messages.sort(key=lambda mes: mes.message_id)
        data["album"] = album_messages
        await handler(event,data)
        del self.album_data[event.media_group_id]