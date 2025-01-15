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
from aiogram.enums import ParseMode
from filters.chat_type import ChatTypeFilter

import db
import services.imageTicketGenerator
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from babel.dates import format_date, format_datetime, format_time
from datetime import timedelta

import xlsxHelper
import os

from filters.any_attachment import AnyAttachmentFilter
from filters.group_id import GroupIdFilter
from states.adminStates import AdminStates
from services import featureToggleService

from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

router = Router()

adminGroupId = config.admin_group.get_secret_value()

callback_hide_event_key = "hideEvent_"
callback_switch_status_callback_key = "switchFt_"
callback_notify = "notify_"

notifyGroupUserDataKey = "notifyGroupKey"

#ответ на запрос помощи пользователем
#обработчик сработает если это ответ на сообщение, и сообщение, на которое отвечают начинается с '[help chatId:messageId]'
@router.message(F.reply_to_message, F.reply_to_message.text.startswith('[help'), GroupIdFilter(adminGroupId))
async def helpRequesReplyHandler(message: Message, bot: Bot):
    ids = message.reply_to_message.text[6:].split(":",1)
    chatId = ids[0]
    messageId = ids[1].split("]")[0]
    try:
        await bot.send_message(chat_id=chatId, reply_to_message_id=messageId, text=message.text)
        await bot.send_message(chat_id=chatId, reply_to_message_id=messageId, text="Если твой вопрос не решен и ты хочешь отправить еще одно сообщение, кликни /help Для продолжения работы с ботом, кликни /start")
        await message.reply(f"Данное сообщение успешно переслано пользователю.")
    except Exception as e:
        await message.reply(f"Во время пересылки сообщения произошла ошибка: {str(e)}")


@router.message(Command(commands=["hide"]), GroupIdFilter(adminGroupId))
async def cmd_hide_event(message: Message, command: CommandObject, bot: Bot):
    events = db.getEvents()
    today = datetime.datetime.today().date()
    events = list(filter(lambda ev: ev.eventDate.date() >= today and ev.hide == False, events))
    builder = InlineKeyboardBuilder()
    for ev in events:
        builder.row(types.InlineKeyboardButton(
            text = f"{ev.id} {ev.name}, {ev.cost}р, {format_datetime(ev.eventDate, 'd MMM HH:mm', locale='ru_RU')}",
            callback_data = f"{callback_hide_event_key}{ev.id}"
        ))
    await message.answer(
        reply_markup=builder.as_markup(),
        text="Выбери мероприятие, что нужно скрыть"
    )

#коллбек на скрытие мероприятия
@router.callback_query(F.data.startswith(callback_hide_event_key))
async def callback_event_selected(callback: types.CallbackQuery, 
                                  internal_user_id: int,
                                  state: FSMContext,
                                  bot: Bot):
    eventId = callback.data.split("_")[1]
    ev = db.hideEvent(eventId)
    await callback.message.edit_text(text=f"Мероприятие {ev.id} '{ev.name}' скрыто пользователем {callback.from_user.full_name}" )
    await callback.answer(text="Мероприятие скрыто!")

@router.message(Command(commands=["ft"]), GroupIdFilter(adminGroupId))
async def cmd_show_ft_status(message: Message, command: CommandObject, bot: Bot):
    fts = db.getFeatureToggles()
    builder = InlineKeyboardBuilder()
    for ft in fts:
        builder.row(types.InlineKeyboardButton(
            text = f"{ft.id}. {ft.name}, '{ft.enabled}' {ft.description}",
            callback_data = f"{callback_switch_status_callback_key}{ft.id}"
        ))
    await message.answer(
        reply_markup=builder.as_markup(),
        text="Значение Фичатогла будет изменено на противоположное"
    )

#уведомление пользователям в личное сообщение
@router.message(Command(commands=["notify"]), GroupIdFilter(adminGroupId))
async def cmd_notify_users(message: Message, 
                             state: FSMContext):
    today = datetime.datetime.now()
    events = db.getEvents()
    events = list(events)
    events = sorted(events, key = lambda ev: ev.eventDate)
    for ev in events:
        if ev.displayUntil is None:
            ev.displayUntil = ev.eventDate + timedelta(hours=3)
    events = filter(lambda x: x.displayUntil > today, events)    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="уведомление всем пользователям",
        callback_data=f"{callback_notify}all"
    ))
    for ev in events:
        builder.row(types.InlineKeyboardButton(
            text = f"{ev.id} {ev.name}, {ev.description}",
            callback_data = f"{callback_notify}{ev.id}"
        ))
    await message.answer(
        reply_markup=builder.as_markup(),
        text="Выберите пользователей, которых нужно уведомить. /cancel для отмены"
    )
    await state.set_state(AdminStates.notify)

@router.message(Command(commands=["cancel"]), StateFilter(AdminStates.notify), GroupIdFilter(adminGroupId))
async def cmd_cancel_notify_users(message: Message, 
                             state: FSMContext):
    await state.set_state(None)
    await state.update_data({notifyGroupUserDataKey: None})
    await message.reply(text="Отлично! Режим ввода уведомления для пользователей отменен! state = None")


@router.callback_query(F.data.startswith(callback_notify))
async def callback_set_notify_group(callback: types.CallbackQuery, 
                                  state: FSMContext,):
    groupOrEventId = callback.data.split("_")[1]
    await state.update_data({notifyGroupUserDataKey: groupOrEventId})

    await callback.message.edit_text(text=f"""[notify]Будет создано уведомление группе '{groupOrEventId}'. 
Текст следущего сообщения от <b>{callback.from_user.full_name}</b> будет перслан пользователям, купившим билет на выбранное мероприятие или всем! 
/cancel для отмены режима ввода уведомления""",
                                      parse_mode=ParseMode.HTML )
    await callback.answer(text="Введи текст уведомления")

#Обработчик AdminStates.notify. В этом состоянии сообщение будет переслано ранее выбранной группе. Хотелось бы дать какое-то время жизни этому методу
@router.message(StateFilter(AdminStates.notify), GroupIdFilter(adminGroupId))
async def notify_users_message(message: Message, 
                               bot: Bot,
                               state: FSMContext):
    userData = await state.get_data()
    if userData.get(notifyGroupUserDataKey, None) == None:
        await message.reply(text="Что-то не так. Отсутсвует группа, которую нужно уведомить в userData. Кликни notify что-бы начать еще раз")
        return 
    try:
        text = message.text
        usersGroup = userData[notifyGroupUserDataKey]
        users = db.getUsers()
        counter = 0
        if usersGroup == "all":
            for user in users:
                        await bot.send_message(
                            text= text,
                            chat_id= user.telegramId
                        )
                        counter +=1
            await message.reply(f"[notify]Отправлено {counter} уведомлений c текстом '{text}'. Уведомление инициировано пользователем {message.from_user.full_name}")
        else:
            tickets = db.getCodeTickets()
            tickets = list(filter(lambda x: x.event_id == int(usersGroup), tickets))
            userIds = map(lambda x: x.user_id, tickets)
            userIds = list(set(userIds))
            for userInternalId in userIds:
                await bot.send_message(
                    text= text,
                    chat_id= next( u for u in users if u.id == userInternalId).telegramId
                )
                counter +=1
            await message.reply(f"[notify]Отправлено {counter} уведомлений c текстом '{text}'. Уведомление инициировано пользователем {message.from_user.full_name}")
    except Exception as e:
        await message.reply(text=f"Во время создания уведомлений произошло исключение {str(e)}")
    await state.update_data({notifyGroupUserDataKey: None})
    await state.set_state(None)

@router.callback_query(F.data.startswith(callback_switch_status_callback_key))
async def callback_switch_ft(callback: types.CallbackQuery, 
                                  internal_user_id: int,
                                  state: FSMContext,
                                  bot: Bot):
    ftId = callback.data.split("_")[1]
    ft = db.switchFtStatus(ftId)
    await callback.message.edit_text(text=f"Значение фичатогла {ft.id} '{ft.name}' изменено на '{ft.enabled}' пользователем {callback.from_user.full_name}. Изменения будет видно через 5 минут!" )
    await callback.answer(text="Фт переключен!")

#ответить пользователю в админ группе, сообщение будет переслано ему лично
@router.message(Command(commands=["generateTicket"], prefix="%"), GroupIdFilter(adminGroupId))
async def cmd_generate_ticket(message: Message, command: CommandObject, bot: Bot):
    errorMessage ="Ошибка: не переданы аргументы. Команда должна выглядеть так: '%generateTicket 115 1', где первое число id - запроса, второе число - количество билетов"
    if command.args is None:
        await message.answer(
          "Не переданы аргументы или бот не смог их распознать"
        )
        return
    try:
        ticketRequestId, countstr = command.args.split(" ", maxsplit=2)
        count = int(countstr)
        ticketRequest = db.getTicketRequest(ticketRequestId)
        if(ticketRequest == None):
            message.answer(f"запрос с идентификатором {ticketRequestId} не найден!")
            return
        event = db.getEvent(ticketRequest.event_id)
        user = db.getUserByInternalId(ticketRequest.user_id)
        counter = 1 
        while counter<= int(count) :
            ticket = imageTicketGenerator.generateTicket(event)
            image = FSInputFile(ticket.ticketFilePath)
            result = await message.answer_photo(
                image,
                #TODO: а тут в капшн всю информацию для проверки
                caption = f"сгенерирован билет {ticket.ticketId} на {event.name} для {user.name}"
            )
            ticket.telegramFileId = result.photo[-1].file_id
            await bot.send_photo(user.telegramId, ticket.telegramFileId)
            db.addCodeTicket(ticket)
            counter+=1
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            text= f"{errorMessage}"
        )
        return

@router.message(GroupIdFilter(adminGroupId), F.text.regexp("\d{4}$"))
async def getTicketInfo(message: Message):
    code = int(message.text)
    tickets = list(db.getCodeTickets())
    ticket = next(filter(lambda t: t.code ==int(code), tickets), None)
    if ticket == None:
        await message.reply(
            text = "Билет не найден!")
        return
    ticketInfo = f"""'{ticket.event.name}'
Контакт: {ticket.contactInformation}
Стоимость: {ticket.cost}
Дата выпуска: {format_datetime(ticket.created, 'd MMM HH:mm', locale='ru_RU')}"""
    await message.reply(
        text= ticketInfo,
    )
        #Обратная совместимость
    if ticket.confirmationType is None:
        confirmationType = ticket.confirmationFileName
    else:
        confirmationType = ticket.confirmationType
    if confirmationType == "image":
            await message.answer_photo( photo=ticket.confirmationFileId, 
                                    caption= f"подтверждение билета {ticket.code}")
            return
    elif confirmationType == "text":
            await message.answer(text=f"Информацией о подтверждении выступало текстовое сообщение {ticket.confirmationFileName}")
            return
    elif confirmationType == "doc":
        await message.answer_document(document= ticket.confirmationFileId,
                                caption= f"подтверждение билета {ticket.code}")
    else:
        await message.answer(text= f"подтверждение билета выступало что-то с типом {confirmationType}")
    

callback_selectEventKey = "callbackGetSummary_"

@router.message(GroupIdFilter(adminGroupId), Command("stat"))
async def getEventsListForStat(message: Message):
    builder = build_inlene_keyboard_for_events()
    await message.answer(text="выберите, статистику по которой вас интересует", 
                         reply_markup=builder.as_markup())

def build_inlene_keyboard_for_events() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    events = db.getEvents()
    #today = datetime.datetime.now()
    #events = list(filter(lambda x: x.eventDate >= today, events))
    for ev in events:
        builder.row(types.InlineKeyboardButton(
            text = f"id:{ev.id} {ev.name}, {ev.cost}р., {ev.eventDate.strftime('%d %b, %H:%M')}",
            callback_data = f"{callback_selectEventKey}{ev.id}"
        ))
    return builder


@router.callback_query(F.data.startswith(callback_selectEventKey))
async def callback_event_selected(callback: types.CallbackQuery):
    eventId = callback.data.split("_")[1]
    selectedEvent = db.getEvent(int(eventId))
    tickets = db.getCodeTickets()
    eventTickets = filter(lambda x: x.event_id == int(eventId), tickets)
    eventTickets = sorted(eventTickets, key= lambda t: t.code)
    if len(eventTickets) < 1:
        await callback.message.answer(text="Увы, билетов продано не было")
        return
    try:
        fileName = f"{datetime.datetime.now().strftime('%m-%d %H %M')}_eventId={eventId}"
        summary = f"Отчет о проданных билетах на {datetime.datetime.now().strftime('%d %b, %H:%M')} для {selectedEvent.id}:'{selectedEvent.name}'"
        resultFile = xlsxHelper.createXlsxForTickets(fileName, eventTickets, summary)
        with open(resultFile, "rb") as document:
            await callback.message.answer_document(
                BufferedInputFile(
                    document.read(),
                    filename=resultFile
                ),
                caption=summary
            )
        os.remove(resultFile)
    except Exception as e:
        await callback.message.answer(
            text=f"Ошибка во время формирования отчета. {repr(e)}")
        raise e
    finally:
        await callback.answer(
            text="Спасибо!",
            show_alert=False
        )

@router.message(Command(commands=["cancel"]), StateFilter(AdminStates.codeCheck))
async def cmd_start(message: Message,
                         bot: Bot,
                         state: FSMContext):
    await state.set_state(None)
    await message.answer("Выхожу из режима проверки кодов. кликни /start,  чтобы начать работу с ботом!")

@router.message(Command(commands=["codeCheck"]), ChatTypeFilter("private"))
async def cmd_code_check(message: Message,
                         bot: Bot,
                         state: FSMContext,
                         ftService: featureToggleService.FeatureToggleService):

    if not ftService.getFeatureToggleState(ftService.checkCodeInPrivateChatFT):
        await message.reply(text="проказник")
        return
    await message.answer(text="Ты в режиме проверки кодов. Набери код без пробелов, чтобы получить по нему информацию. Для выхода из этого режима кликни /cancel")
    await state.set_state(AdminStates.codeCheck)

@router.message(StateFilter(AdminStates.codeCheck), ChatTypeFilter("private"))
async def check_code(message: Message,
                     bot: Bot):
    code = message.text
    try:
        code = int(code)
        await getTicketInfo(message)
    except:
        await message.reply("код не распознан. Если хочешь прекратить режим проверки кодов, кликни /cancel")