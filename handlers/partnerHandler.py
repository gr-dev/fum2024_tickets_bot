from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from config_reader import config
from aiogram.filters.command import CommandObject
from config_reader import config
import db
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from babel.dates import format_date, format_datetime, format_time
from filters.chat_type import ChatTypeFilter
from states.partnerStates import PartnerStates
from aiogram.enums import ParseMode
import os
import re
from filters.any_attachment import AnyAttachmentFilter

from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from states import partnerStrings
from keyboards.simple_row import make_row_keyboard
from codeTicketGenerator import CodeTicketGenerator

contributionSizeUserDataKey = "partner_contributionSize"
contactUserDataKey = "partner_userContact"
contributionTypeDataKey = "partner_contributionType"

adminGroupChatId = config.admin_group.get_secret_value()
PARTNER_EVENT_ID = config.PARTNER_EVENT_ID.get_secret_value()

router = Router()
strings = partnerStrings

@router.message(StateFilter(PartnerStates.contributionType), ChatTypeFilter("private"))
async def state_selecting_contibution_type(message: Message, 
                                      state: FSMContext):
    contributionType = message.text
    await state.update_data({contributionTypeDataKey: contributionType})

    await message.answer(text = strings.getContactInformation,
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnerStates.contactInformation)

@router.message(StateFilter(PartnerStates.contactInformation), ChatTypeFilter("private"))
async def state_getting_contact_information(message: Message, 
                                      state: FSMContext):
    contactInformation = message.text
    items = [
        m.group()#((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}
        for m in re.finditer(r"[\d]{6,10}", contactInformation)
    ]
    if len(items) == 0:
        await message.reply(
            text="Увы, я не смог определить контактный номер телефона в твоем сообщении... Попробуй еще раз, например, Роман, 79501011199 "
        )
        return
    await state.update_data({contactUserDataKey: contactInformation})

    await message.answer(text= strings.inputContributionSize)
    await state.set_state(PartnerStates.contributionSize)

@router.message(StateFilter(PartnerStates.contributionSize), ChatTypeFilter("private"))
async def state_contributeSize_parsing(message: Message, 
                                      state: FSMContext):
    contributionSize = message.text
    try:
        number = int(contributionSize)
    except ValueError:
        await message.reply(text="Увы, я не смог разобраться с этим. Умею работать только с целыми числами, например '10000', или '3600'")
        return
    contributionSize = int(contributionSize)
    await state.update_data({contributionSizeUserDataKey: contributionSize})
    await message.reply(
        text=strings.paymentInformationMessage,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True)
    await state.set_state(PartnerStates.gettingConfirmation)

@router.message(StateFilter(PartnerStates.gettingConfirmation), ChatTypeFilter("private"), AnyAttachmentFilter())
async def state_confirmation_file(message: Message, 
                                      state: FSMContext,
                                      internal_user_id: int,
                                      bot: Bot):
    #TODO: пересылка в админ группу
    #TODO: сохранение информации о вкладе и выписка билетов
    await message.reply(text="Отлично, спасибо!")
    userData = await state.get_data()
    contributionSize = userData[contributionSizeUserDataKey]
    ticketCount = 1
    if int(contributionSize) < 3600:
        messageText = strings.resultLess300
    else:
        messageText = strings.resultMore300
        ticketCount = 2
    await message.answer(
        text=messageText)
    contactInformation = userData[contactUserDataKey]
    contributionType = userData[contributionTypeDataKey]
    summaryMessage = generateCodeTickets(message, ticketCount, internal_user_id, contactInformation, contributionType)
    await resend_message_to_admin_group(message, bot, f"<b>[партнерский билет] {contributionType}</b>, {contactInformation}, заявленная сумма: {contributionSize}. Для партнера выпущены билеты: {summaryMessage}")
    await message.answer(
        text=summaryMessage, 
        parse_mode= ParseMode.HTML
    )
    await message.answer("Для продолжения работы с ботом, кликни /start!")
    await state.clear()

@router.message(StateFilter(PartnerStates.gettingConfirmation), ChatTypeFilter("private"))
async def state_confirmation_text(message: Message, 
                                      state: FSMContext):
    replyText = "Увы, я не могу обработать это сообщение. Я ожидаю подтверждение взноса в виде скриншота или файла. Если хочешь начать работу со мной заново - кликни /start"
    await message.reply(
        text=replyText
    )

from db import CodeTicket, TicketRequest

def generateCodeTickets(message: Message,
                        ticketCount:int,
                        internal_user_id: int,
                        contactInformation: str,
                        contributionType: str) -> str:
    file_id = ""
    file_name = ""
    confirmation_type = ""
    if message.document != None:
        file_id = message.document.file_id
        file_name = message.document.file_name
        confirmation_type ="doc"
    elif message.photo != None:        
        file_id = message.photo[0].file_id
        confirmation_type ="image"
    elif message.content_type == "text":
        file_id = message.content_type
        file_name = message.text
        confirmation_type ="text"
    else:
        file_id = message.content_type
        file_name = message.content_type
        confirmation_type = message.content_type
        request = TicketRequest()
    eventId = PARTNER_EVENT_ID
    i = 0
    requestIds = []
    while i < ticketCount:
         requestIds.append(db.addUserTicketRequest(eventId, internal_user_id, f'[партнер - {contributionType}] {contactInformation}'))
         i+=1
    requests = db.getTicketRequests()
    requests = filter(lambda r: r.id in requestIds, requests)
    ticketInformation = ""
    counter = 1
    for request in requests:
        code = CodeTicketGenerator.generateCodeTicket(eventId)
        ticket = CodeTicket()
        ticket.code = code
        ticket.created = datetime.datetime.now()
        ticket.event_id = request.event_id
        ticket.contactInformation = request.requestDescription
        ticket.user_id = request.user_id
        ticket.cost = request.cost
        ticket.confirmationFileId = file_id
        ticket.confirmationFileName = file_name
        ticket.confirmationType = confirmation_type
        #TODO; оптимизировать количество подключений
        db.addCodeTicket(ticket)
        ticketInformation+=f"{counter}. {request.event.name}, {request.event.description}, {format_datetime(request.event.eventDate, 'd MMM HH:mm', locale='ru_RU')}. Код: <b>{ticket.code}</b> \n"
        counter +=1
    return ticketInformation

#вспомогательный метод для отправки сообщений в группу администраторов
async def resend_message_to_admin_group(messageToForward: Message, bot: Bot, additionalInfo: str = None):
    if str != None:
        await bot.send_message(adminGroupChatId, 
                               additionalInfo, 
                               parse_mode=ParseMode.HTML)
    await bot.forward_message(
        adminGroupChatId, 
        from_chat_id=messageToForward.chat.id,
        message_id=messageToForward.message_id
        )