from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import Message
from models import notificationModel, enum_notificationType
from models.enum_notificationType import NotificationType
import db


#https://botfather.dev/blog/zapusk-funkczij-v-bote-po-tajmeru#integration примеры с настройко apscheduler
class TicketService():

    logTag = "[ticketService]"

    def __init__(self):
        pass

    def isTicketLimitReached(self, eventId: int)-> bool:
        eventId = int(eventId)
        limits = db.getEventTicketsLimit()
        if len(limits) == 0:
            return False
        limit = next(filter(lambda x: x.event_id == eventId, limits), None)
        if limit is None:
            return False
        tickets = db.getCodeTickets()
        tickets = list(filter(lambda t: t.event_id == eventId , tickets))
        if len(tickets) >= limit.count:
            return True
        return False


        