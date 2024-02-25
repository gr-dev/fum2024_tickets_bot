from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import Message

#https://botfather.dev/blog/zapusk-funkczij-v-bote-po-tajmeru#integration примеры с настройко apscheduler
class NotificationService():
    confirmationNotificationTag = "confirmation_notification"

    def __init__(self, sheduler: AsyncIOScheduler, bot: Bot):
        self.sheduler = sheduler
        self.bot = bot
    
    async def sendMessage(self, text: str, chat_id: int):
        await self.bot.send_message(text = text, chat_id= chat_id)

    def addNotificationAboutConfirmation(self, chat_id: int):
        try:
            self.sheduler.add_job(self.sendMessage, 
                    trigger="date", 
                    run_date=datetime.now()+ timedelta(seconds=10),
                    kwargs={'text': "Пришли скриншот или чек в этот чат!", 
                            'chat_id': chat_id},
                    id = f"{self.confirmationNotificationTag}_{chat_id}")
        except Exception as e:
            print(f"[notificationService]{e}")
            
    def removeUserConfirmationNotification(self, chat_id: int):
        try:
            self.sheduler.remove_job(job_id=f"{self.confirmationNotificationTag}_{chat_id}")
        except Exception as e:
            print(f"[notificationService]{e}")