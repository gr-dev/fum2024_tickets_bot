import traceback
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
import db
from db import UpdateLog
    
class CommonMiddleware(BaseMiddleware):

    def get_or_add_internal_user_id(self, user: User, telegramChatId: int) -> int:
        return db.addTelegramUser(user)
    
    def logUpdate(self, update: TelegramObject, telegramChatId: int) -> None:
        logUpdate = UpdateLog()
        logUpdate.update_type = update.event_type
        logUpdate.telegramChatId = telegramChatId
        updateType = update.event_type
        try:
            if updateType=="message":
                #TODO: оказывается, вложения это тоже собщения
                if(update.message.text != None):
                    logUpdate.message = f"[message.text]{update.message.text}"
                    logUpdate.telegramTimeStamp = update.message.date
                elif update.message.document != None:
                    logUpdate.message = f"[message.document.file_name]{update.message.document.file_name}"
                    logUpdate.telegramTimeStamp = update.message.date
                elif update.message.photo != None:
                    logUpdate.message = f"[message.photo[0].file_id]{update.message.photo[0].file_id}"
                    logUpdate.telegramTimeStamp = update.message.date
            elif updateType == "callback_query":
                logUpdate.message = f"[callback_query.data]{update.callback_query.data}"
            else:
                logUpdate.message = "not implemented event_type"
            db.addUpdateLog(logUpdate)
        except Exception as e:
            logUpdate.message = f"[exception in CommonMiddleware.logUpdate] {str(e)}"
            logUpdate.exceptionMessage = f"{str(e)} {''.join(traceback.TracebackException.from_exception(e).format())}" 
            db.addUpdateLog(logUpdate)


    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        self.logUpdate(event, data["event_chat"].id)
        user = data["event_from_user"]
        data["internal_user_id"] = self.get_or_add_internal_user_id(user, data["event_chat"].id)
        try:
            result =  await handler(event, data)
        except Exception as e:
            logUpdate = UpdateLog()
            logUpdate.update_type = event.event_type
            logUpdate.telegramChatId =  data["event_chat"].id
            logUpdate.exceptionMessage = f"{str(e)} {''.join(traceback.TracebackException.from_exception(e).format())}" 
            print(logUpdate.exceptionMessage)
            db.addUpdateLog(logUpdate)
            raise e
        return result