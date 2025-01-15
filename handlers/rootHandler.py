import datetime
from datetime import timedelta
import time
import re
from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject
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
from aiogram.utils.deep_linking import decode_payload


import db
from db import CodeTicket
from codeTicketGenerator import CodeTicketGenerator

from config_reader import config
from keyboards.simple_row import make_row_keyboard, make_vertical_keyboard
from filters.any_attachment import AnyAttachmentFilter
from filters.chat_type import ChatTypeFilter
from stringHelper import CommonHandlerStringHelper, MessageType
from states.orderStates import OrderStates
from states.partnerStates import PartnerStates
from states.rootStates import RootStates

from states import partnerStrings
from handlers import commonHandler
import stringHelper

from services import featureToggleService

router = Router()

#команды для кнопок
btn_myTickets = "Мои билеты" #Отображение моих билетов. Обработчик определен в userHandler
btn_needHelp = "Нужна помощь или другая проблема с билетами"
btn_partner = partnerStrings.buttonInMainMenu

#TODO: избавиться бы от этого хелпера
stringHelper = CommonHandlerStringHelper()


#обработка команды /start, построение начального меню
@router.message(Command(commands=["start"]), ChatTypeFilter("private"))
async def cmd_start(message: Message, 
                    state: FSMContext,
                    internal_user_id: int,
                    ftService: featureToggleService.FeatureToggleService,
                    command: CommandObject = None):
    #TODO: входящие параметры обрабатывать без исключений
    try:
        args = command.args
        if args is not None:
            payload = decode_payload(args)
    except: 
        pass
    await state.clear()
    #отменяю все запросы, кроме тех что уже помечены как оплаченные
    db.cancelUserticketRequestsExcludeCompleted(internal_user_id)
    eventsGroup = db.getEventGroups()
    actualGroups = list(filter(lambda t: t.hide == False, eventsGroup))

    replyKeyboard = make_vertical_keyboard(map(lambda x: x.name, actualGroups))
    replyKeyboard.row(KeyboardButton(text=btn_myTickets))
    #партнерский вклад
    if (ftService.getFeatureToggleState(ftService.partnerContributeShowInMainMenu)):
        replyKeyboard.row(KeyboardButton(text=btn_partner))
    #запрос помощи
    replyKeyboard.row(KeyboardButton(text=btn_needHelp))

    await message.answer(
        text=stringHelper.GetText(MessageType.HellowMessage),
        #TODO: не выводить группы, в которых нет эвентов
        reply_markup=replyKeyboard.as_markup(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RootStates.mainMenu)

#Обработка выбора "партнерский вклад"
@router.message(ChatTypeFilter("private"), F.text == btn_partner)
async def btn_menu_partner(message: Message, 
                        state: FSMContext):
    await message.answer(
        text=partnerStrings.startMessage
    )
    answers = [partnerStrings.anonimousContributionBtn, partnerStrings.publicContributionBtn]
    await message.answer(
        text=partnerStrings.contributionType,
        reply_markup= make_row_keyboard(answers)
    )
    await state.set_state(PartnerStates.contributionType)

#обработка запроса помощи
@router.message(ChatTypeFilter("private"), F.text == btn_needHelp)
async def btn_menu_need_help(message: Message, 
                    state: FSMContext):
    await message.answer(
        text="Что случилось? Опиши подробно свою проблему одним сообщением, я перешлю его своим коллегам и мы постарается тебе помочь как можно быстрее! <b>Также, пожалуйста, укажи контактный номер!</b>, иначе в некоторых случаях мы не сможем связаться с тобой",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML
    )
    # обработчик в commonHandler
    await state.set_state(OrderStates.help)

@router.message(ChatTypeFilter("private"), Command("help"))
async def cmd_help(message: Message, 
                    state: FSMContext):
    await btn_menu_need_help(message, state)

#обработка запроса Мои билеты
@router.message(ChatTypeFilter("private"), F.text == btn_myTickets)
async def btn_menu_myTickets(message: Message, 
                    internal_user_id: int):
    tickets = db.getCodeTickets()
    today = datetime.datetime.today().date()
    actualTickets = list(filter(lambda t: t.event.eventDate.date() >= today and t.user_id == internal_user_id, tickets))
    if len(actualTickets) == 0:
        await message.answer(
            text="Увы, актуальных билетов нет! Кликни /start чтобы приступить к покупке!"
                    )
        return
    actualTickets = sorted(actualTickets, key = lambda ticket: ticket.event.eventDate)
    ticketsSummary = ""
    counter = 1
    for t in actualTickets:
        ticketsSummary+= f"{counter}. {t.event.name}, {format_datetime(t.event.eventDate, 'd MMM HH:mm', locale='ru_RU')}, код: <b>{t.code}</b>\n"
        counter+=1
    await message.answer(
        text=ticketsSummary,
        parse_mode=ParseMode.HTML
    )

#по хорошему, оставшееся - выбор eventGroup (eventGroup)
@router.message(StateFilter(RootStates.mainMenu), ChatTypeFilter("private"))
async def select_event_group(message: Message, 
                            state: FSMContext):
    #TODO: оптимизировать, избавиться от обращений в базу
    eventsGroup  = db.getEventGroups()
    eventsGroup = list(eventsGroup)
    selectedEventGroup = next(filter(lambda x: x.name == message.text, eventsGroup), None)
    if selectedEventGroup is None:
        await message.reply(
            text="Увы, я не смог обработать твой запрос. Выбери один из пунктов меню, пожалуйста, или нажми /start")
        return
    await commonHandler.state_selecting_event_group(message, state)

#обработчик на случай, если все остальные не отработали
@router.message(StateFilter(None), ChatTypeFilter("private"))
async def no_state(message: Message):
    await message.answer("Привет! Для начала работы с ботом нажми /start В случае если у вас проблема с купленным и оплаченным билетом, нажми /help")