import datetime
from datetime import timedelta
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
from services import googleSheetsService
from services import featureToggleService

import db
from db import CodeTicket
from codeTicketGenerator import CodeTicketGenerator

from config_reader import config
from keyboards.simple_row import make_row_keyboard, make_vertical_keyboard
from filters.any_attachment import AnyAttachmentFilter
from filters.chat_type import ChatTypeFilter
from stringHelper import CommonHandlerStringHelper, MessageType
from states.orderStates import OrderStates
from handlers import rootHandler

router = Router()

stringHelper = CommonHandlerStringHelper()

def getEvents():
    return db.getEvents()

#команды для кнопок
cmd_btn_create_order = 'Оформить заказ'
cmd_btn_recreate_order = "Оформить заказ заново"
cmd_btn_confirm ="Все верно!"
cmd_btn_gettingContact_use_old_contact ="Да, контакт тот же"
cmd_btn_correct_details = "Исправить"

adminGroupChatId = config.admin_group.get_secret_value()

#ключи для userData
userData_orderDetalisKey = "orderDetails"
userData_selectedEventGroupId = "eventGroupSelected"
userData_requestSummInrubles = "requestSummInrubles"
userData_freeEvent = "freeEvent"
userData_orderSummaryMessage = "userData_orderSummaryMessage" #идентификатор сообщения для summary сообщения

#ключи для коллбэков (inline кнопок)
#ключ для @callback_event_selected
callback_selectEventKey="selectedEvent_"
callback_userRatingKey="rating_"
callback_switchGroup="switchGroup_"

#вспомогательный метод для построения inline-кнопок
def build_inlene_keyboard_for_event_group(events: list) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for ev in events:
        builder.row(types.InlineKeyboardButton(
            text = f"{ev.name}, {ev.cost}р, {format_datetime(ev.eventDate, 'd MMM HH:mm', locale='ru_RU')}",
            callback_data = f"{callback_selectEventKey}{ev.id}"
        ))
    return builder

#возвращает не скрытые эвенты принадлежащей указанной группе
def get_actual_events(groupId: int):
    today = datetime.datetime.now()
    events = getEvents()
    events = list(events)
    events = sorted(events, key = lambda ev: ev.eventDate)
    for ev in events:
        if ev.displayUntil is None:
            ev.displayUntil = ev.eventDate + timedelta(hours=3)
    groupEvents = filter(lambda x: x.eventGroupId == groupId and x.displayUntil > today and x.hide == False, events)
    return groupEvents

#вспомогательный метод для построения inline навигации - мероприятия и переход к другим группам
def build_event_keyboard(groupId: int):
    groupEvents = get_actual_events(groupId)
    builder = build_inlene_keyboard_for_event_group(groupEvents)
    allGroups = db.getEventGroups()
    selectedGroup = next(filter(lambda g: g.id == groupId , allGroups), None)
    for group in allGroups:
        if group.id == groupId or group.hide == True or group.paymentInfo_id != selectedGroup.paymentInfo_id: # последнее условие для того чтобы избежать конфликта, если реквизиты разные
            continue
        #если в группе нет актуальных мероприятий, то ее не отображать
        exist = next(filter(lambda ev: ev.hide == False and ev.eventDate >= datetime.datetime.today() , group.events), None)
        if exist is None:
            continue
        builder.row(types.InlineKeyboardButton(
                text = f"К мероприятиям '{group.name}'",
                callback_data = f"{callback_switchGroup}{group.id}"
            ))
    return builder

#выбор категории мероприятий (eventGroup)
@router.message(StateFilter(OrderStates.eventGroupSelection), ChatTypeFilter("private"))
async def state_selecting_event_group(message: Message, 
                                      state: FSMContext):
    eventsGroup  = db.getEventGroups()
    eventsGroup = list(eventsGroup)
    selectedEventGroup = next(filter(lambda x: x.name == message.text, eventsGroup), None)
    replyKeyboard = make_vertical_keyboard(map(lambda x: x.name, eventsGroup))
    if selectedEventGroup == None:
        await message.answer(
          text="Что-то не так, попробуйте еще раз, нажав на одну из кнопок меню!",
          reply_markup=replyKeyboard.as_markup())
        return
    await state.update_data({userData_selectedEventGroupId: selectedEventGroup.id})
    answers = [cmd_btn_create_order, cmd_btn_recreate_order]
    await message.answer(
        text=f"Можно купить билеты сразу на несколько мероприятий. По завершению, кликни \"{cmd_btn_create_order}\"",
        reply_markup=make_row_keyboard(answers)
    )
    builder = build_event_keyboard(selectedEventGroup.id)
    await message.answer(
        text=stringHelper.GetText(MessageType.SelectingEvent),
        reply_markup=builder.as_markup()
    )
    await state.set_state(OrderStates.eventSelection)

#обработчик StateFilter(OrderStates.eventGroupSelection)
@router.callback_query(StateFilter(OrderStates.eventSelection), F.data.startswith(callback_selectEventKey))
async def callback_event_selected(callback: types.CallbackQuery, 
                                  internal_user_id: int,
                                  state: FSMContext,
                                  bot: Bot):
    eventId = callback.data.split("_")[1]
    db.addUserTicketRequest(eventId, internal_user_id)
    userRequests = db.getTicketRequests()
    userRequests = filter(lambda x: x.user_id == internal_user_id and x.status == 0, userRequests)

    eventsSelected = {}
    #вспомогательная переменная для вывода всплывающего окошка
    for r in userRequests:
        exist = eventsSelected.get(r.event.name, False)
        if exist:
            eventsSelected[r.event.name] = eventsSelected[r.event.name] + 1
        else:
            eventsSelected[r.event.name] = 1
    resultSummary = f"Ты выбрал:\n"
    for key in eventsSelected:
        resultSummary+= f" {key} : <b> {eventsSelected[key]} билет(а\ов) </b>\n"
    userData = await state.get_data()
    if userData_orderSummaryMessage in userData.keys():
        await bot.edit_message_text(message_id = userData[userData_orderSummaryMessage],
                            chat_id=callback.message.chat.id,
                            text=resultSummary,
                            parse_mode=ParseMode.HTML)
    else:
        summaryMessage = await callback.message.answer(text=resultSummary, parse_mode=ParseMode.HTML)
        await state.update_data({userData_orderSummaryMessage: summaryMessage.message_id })

    await callback.answer(
            text="Отлично! Можно сразу купить несколько билетов, кликнув на мероприятие еще раз!",
            show_alert=False
    )

#возможность перейти в другую. ожидается id группы параметром
@router.callback_query(StateFilter(OrderStates.eventSelection), F.data.startswith(callback_switchGroup))
async def callback_switch_group(callback: types.CallbackQuery):
    groupId = callback.data.split("_")[1]
    builder = build_event_keyboard(int(groupId))
    await callback.message.edit_text(
        text=callback.message.text,
        reply_markup=builder.as_markup()
    )

#подтверждение заказа с экрана выбора эвентов
@router.message(StateFilter(OrderStates.eventSelection), ChatTypeFilter("private"), F.text == cmd_btn_create_order )
async def cmd_confirm_selected(message: Message, 
                               state: FSMContext,
                               internal_user_id: int):
    activeTicketRequests = db.getTicketRequests()
    activeTicketRequests = list(filter(lambda r: r.user_id == internal_user_id and r.status == 0, activeTicketRequests))
    if len(activeTicketRequests) == 0:
        await message.answer(text="Не выбрано ни одного мероприятия!")
        return
    #Подсчет количества запросов на билеты для красоты
    eventRequestCountDict = {}
    for r in activeTicketRequests:
        exist = eventRequestCountDict.get(r.event.id, False)
        if exist:
            eventRequestCountDict[r.event.id] = eventRequestCountDict[r.event.id] + 1
        else:
            eventRequestCountDict[r.event.id] = 1
    #итоговое сообщение
    requestSummary = "Давай подведем итоги. Пожалуйста проверь:\n"
    summ = 0
    counter = 0
    for key, value in eventRequestCountDict.items():
        counter +=1
        r = next(filter(lambda x: x.event.id == key, activeTicketRequests))
        requestSummary+=f"{counter}. <b>{r.event.name}</b>, {r.cost}р, {format_datetime(r.event.eventDate, 'd MMM HH:mm', locale='ru_RU')}, {r.event.description}. {value} билета(ов)\n"
    # сумма заказа   
    for r in activeTicketRequests:
        summ = summ + r.cost
    requestSummary+= f"На сумму: <b>{summ}р.</b> \n Все верно?"
    #костыль для бесплатных мероприятий. чтобы не требовать подтверждения
    if summ == 0:
        await state.update_data({userData_freeEvent: True})
    #вспомогательные данные для отображение при запросе информации об оплате
    await state.update_data({userData_requestSummInrubles: summ})
    answers = [cmd_btn_confirm, cmd_btn_recreate_order]
    await message.answer(
        text=requestSummary,
        reply_markup=make_row_keyboard(answers),
        parse_mode=ParseMode.HTML
    )

#оформить корзину заново на этапе выбора эвентов
@router.message(StateFilter(OrderStates.eventSelection), ChatTypeFilter("private"), F.text == cmd_btn_recreate_order )
async def cmd_back_to_start(message: Message, state: FSMContext, internal_user_id: int, ftService: featureToggleService.FeatureToggleService ):
    await rootHandler.cmd_start(message, state, internal_user_id, ftService )

#подтвердить набранную корзину
@router.message(StateFilter(OrderStates.eventSelection), ChatTypeFilter("private"), F.text == cmd_btn_confirm )
async def cmd_confirm_requests_and_go_to_details(message: Message, 
                                                 state: FSMContext,
                                                 internal_user_id: int):
    tickets = db.getUserTickets(internal_user_id)
    if(len(tickets) > 0):
        lastTicket = next(iter(sorted(tickets, key = lambda ticket: ticket.created, reverse=True)), None)
        #если человек ранее покупал билеты, беру ранее введенную контактную информацию
        await state.update_data({userData_orderDetalisKey: lastTicket.contactInformation})
        await message.answer(
            text= f"""Ранее ты указывал контактную информацию как: <b>{lastTicket.contactInformation}</b>? 
Если все верно, кликни '{cmd_btn_gettingContact_use_old_contact}' 
Если хочешь указать другую контактную информацию, кликни '{cmd_btn_correct_details}'""",
            parse_mode=ParseMode.HTML,
            reply_markup=make_row_keyboard([cmd_btn_gettingContact_use_old_contact, cmd_btn_correct_details ])
        )
    else:
        await message.answer(
            text=stringHelper.GetText(MessageType.GetUserInfo),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.HTML
        )
    await state.set_state(OrderStates.orderDetailsGetting)

#подтверждение введеных данных пользователем, переход в OrderStates.paymentAwaiting
@router.message(StateFilter(OrderStates.orderDetailsGetting), ChatTypeFilter("private"), F.text == cmd_btn_confirm)
async def cmd_confirm_orderDetails(message: Message, 
                              state: FSMContext,
                              internal_user_id: int,
                              bot: Bot):
    userData = await state.get_data()
    db.confirmUserRequests(internal_user_id, userData[userData_orderDetalisKey])
    #костыль для бесплатных мероприятий
    if userData_freeEvent in userData.keys(): 
        freeMessage = await message.answer(
            reply_markup=ReplyKeyboardRemove(),
            text="Отлично! Данные мероприятия бесплатны, работаю над билетами!"
        )
        await state_paymentConfirmation(freeMessage, state, internal_user_id, bot)
        return
    else:
        userRequests = db.getTicketRequests()
        userRequests = filter(lambda x: x.user_id == internal_user_id and x.status == 1, userRequests)
        userRequests = list(userRequests)
        #проверка, что реквизиты для всей корзины одни.
        paymentInfoIds = []
        for g in userRequests:
            paymentInfoIds.append(g.event.eventGroup.paymentInfo_id)
        #distinct
        paymentInfoIds = list(set(paymentInfoIds))
        #если реквизитов более одного
        if(len(paymentInfoIds) > 1):
            await message.reply(
                text="Увы, я не могу обработать этот запрос. Пожалуйста, кликни /start и оформи билеты еще раз." 
            )
            return
        paymentMessage = userRequests[0].event.eventGroup.paymentInfo.message
        await message.answer(
            text=f"Реквизиты для оплаты: {paymentMessage}",
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True
        )
        await message.answer(
            text=stringHelper.GetText(MessageType.AwaitingPaymentMessage),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    await state.set_state(OrderStates.paymentAwaiting)

#возвожность исправить контактные данные
@router.message(StateFilter(OrderStates.orderDetailsGetting), ChatTypeFilter("private"),F.text == cmd_btn_correct_details)
async def cmd_edit_orderDetails(message: Message, 
                              state: FSMContext,
                              internal_user_id: int):
    await message.answer(
        text=stringHelper.GetText(MessageType.GetUserInfo),
        reply_markup=ReplyKeyboardRemove()
    )

#пользователь подтвердил использование старых контактных данных
@router.message(StateFilter(OrderStates.orderDetailsGetting), ChatTypeFilter("private"), F.text == cmd_btn_gettingContact_use_old_contact)
async def cmd_use_old_contact_information(message: Message,
                                           state: FSMContext):    
    userData = await state.get_data()
    summ = userData[userData_requestSummInrubles]
    await message.answer(
        text = f"""Отлично! Давай проверим! 
Контактная информация: "{userData[userData_orderDetalisKey]}".
Билеты на сумму {summ} р.
Если хочешь исправить контактную информацию, кликни '{cmd_btn_correct_details}'.
Если все верно, кликни '{cmd_btn_confirm}'. 
Если все надоело и хочешь начать с чистого листа - кликни /start""",
        reply_markup=make_row_keyboard([cmd_btn_confirm, cmd_btn_correct_details ])
    )

#обработка контактных данных пользователя
@router.message(StateFilter(OrderStates.orderDetailsGetting), ChatTypeFilter("private"))
async def state_getting_order_details(message: Message, state: FSMContext):
    userMessage = message.text
    items = [
        m.group()#((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}
        for m in re.finditer(r"[\d]{6,10}", userMessage)
    ]
    if len(items) == 0:
        await message.reply(
            text="Увы, я не смог определить контактный номер телефона в твоем сообщении... Попробуйте еще раз, например, Георгий Победоносцев, 89642888888 "
        )
        return

    await state.update_data({userData_orderDetalisKey: message.text})
    userData = await state.get_data()
    summ = userData[userData_requestSummInrubles]
    await message.answer(
        text = f"""Отлично! Давай проверим! 
Контактная информация: "{message.text}".
Билеты на сумму {summ} р.
Если хочешь исправить контактную информацию, кликни '{cmd_btn_correct_details}'.
Если все верно, кликни '{cmd_btn_confirm}'. 
Если все надоело и хочешь начать с чистого листа - кликни /start""",
        reply_markup=make_row_keyboard([cmd_btn_confirm, cmd_btn_correct_details ])
    )

@router.message(StateFilter(OrderStates.paymentAwaiting), AnyAttachmentFilter(), ChatTypeFilter("private"))
async def state_paymentConfirmation(message: Message, 
                           state: FSMContext,
                           internal_user_id: int,
                           bot: Bot):
    messageToUpdate = await message.answer(
        text="Супер! Минутку! Готовлю билеты!")
    busket = db.getTicketRequests()
    busket = filter(lambda x: x.user_id == internal_user_id and x.status == 1, busket)
    busket = list(busket)
    if len(busket) == 0:
        await message.reply(
            text= "Что-то идет не так! я не нашел активных заявок от вас! Возможно билеты уже были куплены выше? Если хотите оформить еще билеты, кликните /start"
        )
        return
    ticketInformation = ""
    ticketRequestIdsToCompled = list()
    file_id = ""
    file_name = ""
    confirmation_type = ""
    if message.document != None:
        file_id = message.document.file_id
        file_name = message.document.file_name
        confirmation_type ="doc"
    elif message.photo != None:        
        file_id = message.photo[0].file_id
        #TODO: какая-то фигня с фотографиями
        #file_name = "image"
        confirmation_type ="image"
    #костыль для бесплатных билетов
    elif message.content_type == "text":
        file_id = message.content_type
        file_name = message.text
        confirmation_type ="text"
    else:
        file_id = message.content_type
        file_name = message.content_type
        confirmation_type = message.content_type
    counter = 0
    for request in busket:
        counter+=1
        code = CodeTicketGenerator.generateCodeTicket(request.event_id)
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
        ticket.event = request.event
        ticket.user = request.user
        #TODO; оптимизировать количество подключений
        db.addCodeTicket(ticket)
        ticketInformation+=f"{counter}. {request.event.name}, {request.cost}р., {request.event.description}, {format_datetime(request.event.eventDate, 'd MMM HH:mm', locale='ru_RU')}. Код: <b>{ticket.code}</b> \n"
        ticketRequestIdsToCompled.append(request.id)
        #TODO: в будущем, можно было бы сократить количество подключений
        try:
            googleSheetsService.addCodeTicket(ticket)
        except Exception as e:
            messageToAdminGroup = f"[commonHandler, createTicket]при записи в гугл таблицу произошла ошибка: {str(e)}"
            await bot.send_message(adminGroupChatId, messageToAdminGroup, parse_mode=ParseMode.HTML)
    db.completeTicketRequests(ticketRequestIdsToCompled)
    
    #await message.answer(stringHelper.GetText(MessageType.ConfirmationMessage))
    await messageToUpdate.edit_text(stringHelper.GetText(MessageType.ConfirmationMessage))
    await message.answer(text=ticketInformation,
                         parse_mode=ParseMode.HTML)
    await message.answer(text= "Если хочешь оформить еще билеты, кликни /start")
    userName = message.from_user.full_name
    if message.from_user.username is not None:
        userName +=f" @{message.from_user.username}"
    await resend_message_to_admin_group(messageToForward=message,
                                        bot=bot, 
                                        additionalInfo= f"""Куплены билеты:
telegram: {userName}
Контакт: {busket[0].requestDescription}
Билеты:\n {ticketInformation}""")

    await state.set_state(OrderStates.completedOrder)
    #Сбор обратной связи. Можно было бы фичатоглы запилить
    if False:
        builder = InlineKeyboardBuilder()
        marks = { 3: "Супер! Было удобно и понятно!", 2: "Нормально, но можно и лучше", 1: "Не понравилось!"}
        for mark in marks:
            builder.row(types.InlineKeyboardButton(
                text = marks[mark],
                callback_data = f"{callback_userRatingKey}{mark}"
            ))
        await message.answer(
            text="Оцени удобство работы с ботом, пожалуйста!",
            reply_markup= builder.as_markup()
        )


@router.message(StateFilter(OrderStates.paymentAwaiting), ChatTypeFilter("private"))
async def text_in_awaiting_payement(message: Message, 
                           state: FSMContext,
                           internal_user_id: int):
    await message.reply(text="Привет! Отправь подтверждение оплаты - скриншот или документ! Если хочешь оформить заказ заново, отменив текущий - кликни /start")

@router.message(StateFilter(OrderStates.completedOrder), ChatTypeFilter("private"))
async def replay_completedOrderState(message: Message, state: FSMContext, bot: Bot):
    await message.reply(
        text="""Привет! Если хочешь оформить еще билеты, кликни /start.  
В случае возникновения вопросов или проблем, кликни /help и опиши свою проблему в одном сообщении, я передам это соообщение своей команде. Хорошего дня!"""
    )

@router.message(StateFilter(OrderStates.help), ChatTypeFilter("private"))
async def cmd_get_help(message: Message, state: 
                       FSMContext, 
                       bot: Bot,
                       internal_user_id: int):
    await resend_message_to_admin_group(message, bot, f"[help] Пользователь {message.from_user.full_name} запросил помощь:")
    tickets = db.getCodeTickets()
    userTickets =list(filter(lambda t: t.user_id == internal_user_id, tickets))
    actualTickets = sorted(userTickets, key = lambda ticket: ticket.created, reverse=True)
    summary = ""
    if(len(list(actualTickets))> 5):
        summary = "Последние 5 билетов по дате оформления:\n"
        actualTickets = actualTickets[-5:]
    counter = 1
    for t in actualTickets:
        summary+= f"{counter}. {t.event.name}, контакт: '{t.contactInformation}', выпущен: {format_datetime(t.created, 'd MMM HH:mm', locale='ru_RU')}, код: {t.code}\n"
        counter+=1
    if summary !="":
        await bot.send_message(chat_id=adminGroupChatId, 
                    text=summary,
                        parse_mode=ParseMode.HTML)
    await message.reply(
        text="Спасибо! Передаю информацию своим  коллегам, постараемся решить в ближайшее время! Для начала работы с ботом кликни /start"
    )
    await state.clear()

@router.callback_query(F.data.startswith(callback_userRatingKey))
async def callback_rate_bot(callback: types.CallbackQuery, 
                                  internal_user_id: int,
                                  state: FSMContext):
    userRating = callback.data.split("_")[1]
    rating = db.UserRating()
    rating.user_id = internal_user_id
    rating.timestamp = datetime.datetime.now()
    rating.value = int(userRating)
    db.addUserRating(rating)
    await callback.message.edit_text(
        text="Спасибо за оценку!"
    )
    await callback.answer(
        text="Спасибо!"
    )

#вспомогательный метод для отправки сообщений в группу администраторов
async def resend_message_to_admin_group(messageToForward: Message, bot: Bot, additionalInfo: str = None):
    if str != None:
        await bot.send_message(adminGroupChatId, additionalInfo, parse_mode=ParseMode.HTML)
    await bot.forward_message(
        adminGroupChatId, 
        from_chat_id=messageToForward.chat.id,
        message_id=messageToForward.message_id
        )