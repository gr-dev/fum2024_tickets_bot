from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import Message
from models import notificationModel, enum_notificationType
from models.enum_notificationType import NotificationType
import db


#https://botfather.dev/blog/zapusk-funkczij-v-bote-po-tajmeru#integration примеры с настройко apscheduler
class NotificationService():

    logTag = "[notificationService]"

    def __init__(self, sheduler: AsyncIOScheduler, bot: Bot):
        self.sheduler = sheduler
        self.bot = bot
        self.initTasksFromDb()
        self.initTodayNotifications()
        #ежедневное добавление уведомлений о мероприятиях на текущий день
        trigger = CronTrigger(year="*", month="*", day="*", hour="1", minute="0", second="0")
        self.sheduler.add_job(
            self.initTodayNotifications,
            trigger=trigger,
            args= None,
            name="daily initTodayNotifications",
            )
    
    async def __sendMessage(self, text: str, chat_id: int):
        try:
            await self.bot.send_message(text = text, chat_id= chat_id)
        except Exception as e:
            print(f"{self.logTag} exception when sending message: {str(e)}")

    #добавить напоминание о необходимости отправить подтверждение. через 5 минут
    def addPaymentConfirmationNotification(self, chat_id: int):
        run_date=datetime.now()+ timedelta(300)
        job_id = f"{chat_id}_{NotificationType.sendConfirmation.value}"
        self.__addNotification(chat_id, "После оплаты, отправь подтверждение - скриншот или файл - прямо в этот чат!", run_date, job_id)

    def removePaymentConfirmationNotification(self, chat_id: int):
        try:
            job_id = f"{chat_id}_{NotificationType.sendConfirmation.value}"
            #TODO: если этого уведомления нет?
            self.__removeNotification(job_id)
        except Exception as e:
            print(f"{self.logTag}{e}")

    def __addNotification(self, chat_id: int, message: str, notificationDate: datetime, jobId: str):
        try:
            if notificationDate < datetime.now():
                raise ValueError("notificationDate is in past")
            if self.sheduler.get_job(jobId) is not None:
                print(f"{self.logTag} job with id {jobId} already exist")
                return
            self.sheduler.add_job(self.__sendMessage, 
                    trigger="date", 
                    run_date=notificationDate,
                    kwargs={'text': message, 
                            'chat_id': chat_id},
                    #TODO: потенциальный конфликт идентификаторов, например, если мероприятий будет несколько
                    id = jobId)
        except Exception as e:
            print(f"{self.logTag} exception whe addNotificationToSheduler: {str(e)}")
            raise e
            
    def __removeNotification(self, job_id: str):
            self.sheduler.remove_job(job_id=job_id)

    #TODO: восстанавливать уведомления из БД
    def initTasksFromDb(self):
        pass

    #сгенерировать уведомления на сегодняшние мероприятия
    def initTodayNotifications(self):
        print(f"{self.logTag} running of initTodayNotifications")
        todayEvents = db.getCodeTickets()
        users = db.getUsers()
        today = datetime.today()
        for ticket in todayEvents:
            if ticket.event.eventDate.date() == today.date() and ticket.event.eventDate.timestamp() > today.timestamp():
                notificationDate = ticket.event.eventDate - timedelta(hours=1)
                user = next(filter(lambda x: x.id == ticket.user_id, users))
                try:
                    jobId = f"{NotificationType.eventSoon.value}_{user.telegramId}_{notificationDate.timestamp()}"
                    self.__addNotification(user.telegramId, 
                                           f"Привет! Чтобы не пришлось искать код на мероприятие `{ticket.event.name}`, вот он: {ticket.code}", 
                                           notificationDate, 
                                           jobId)
                except Exception as e:
                    print(f"{self.logTag} exception when initTodayNotifications: {str(e)}")
