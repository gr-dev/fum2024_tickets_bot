from datetime import timedelta
import datetime
import time
import re
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from babel.dates import format_date, format_datetime, format_time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services import googleSheetsService

import db
from db import CodeTicket
from codeTicketGenerator import CodeTicketGenerator

from config_reader import config
from keyboards.simple_row import make_row_keyboard, make_vertical_keyboard
from filters.any_attachment import AnyAttachmentFilter
from filters.chat_type import ChatTypeFilter
from stringHelper import CommonHandlerStringHelper, MessageType
from services import featureToggleService, notificationService

from services.featureToggleService import FeatureToggleService

router = Router()

#TODO: добавить бы кеш какой-нибудь, подойдет даже в памяти
stringHelper = CommonHandlerStringHelper()
def getEventGroups():
    return db.getEventGroups()

@router.message(Command(commands=["test"]))
#@router.message(ChatTypeFilter("private"), F.text == "Мои билеты")
async def cmd_test (message: Message, 
                    internal_user_id: int,
                    notificationService: notificationService.NotificationService,
                    ftService: FeatureToggleService):
    result = ftService.getFeatureToggleState(ftService.exampleFeatureToggle)
    print(result)


def shedulerExamples():
    def printValue(message: str = "default message"):
        print(f"[appschedulerService]{message}")

    sheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    #текущее время + десять секунд
    sheduler.add_job(printValue, 
                     trigger="date", 
                     run_date=datetime.now()+ timedelta(seconds=10),
                     kwargs={'message': "hellow from 10 seconds"})
    #по расписанию
    sheduler.add_job(printValue, 
                     trigger='cron', 
                     hour = datetime.now().hour, 
                     minute = datetime.now().minute+1, 
                     start_date=datetime.now())
    # интегравал
    sheduler.add_job(printValue,
                     trigger='interval',
                     seconds=60,
                     kwargs={'message': "message from interwal"})
    sheduler.start()