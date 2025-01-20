from typing import Any, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

class GroupIdFilter(BaseFilter):
    def __init__(self, chatId: int):
        self.chatId = chatId
        
    async def __call__(self, message: Message) -> bool:
        #костыль с преобразование chatID!
        if message.chat.id == int(self.chatId):
            return True
        return False