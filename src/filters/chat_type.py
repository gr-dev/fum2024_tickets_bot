from typing import Any, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

#https://mastergroosha.github.io/aiogram-3-guide/filters-and-middlewares/
class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool: 
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
        

          