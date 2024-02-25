from typing import Any, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

#TODO: наверное, это в мидлвэа должно быть
#https://mastergroosha.github.io/aiogram-3-guide/filters-and-middlewares/
class AnyAttachmentFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool: 
        if  message.document is not None or   message.photo is not None:
            return True
        return False

          