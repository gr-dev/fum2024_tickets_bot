#устаревший метод
@router.message(StateFilter(OrderStates.eventSelection), ChatTypeFilter("private"), F.text.lower() == "legacy")
async def cmd_select_event(message: Message, state: FSMContext):
    selectedEvent = next(filter(lambda x: x.name == message.text, events), None)
    if selectedEvent == None:
        await message.answer(
          text="Увы, я не знаю такого мероприятия, выберите еще раз!",
          reply_markup=make_row_keyboard(list(map(lambda x: x.name, events))))
        return
    await state.update_data(eventId = selectedEvent.id)
    await state.update_data(eventName = selectedEvent.name)
    await message.answer(
        # тут может бытьи нформация или ссылки о самих мероприятиях, добавить информацию о помощи
        text=f"""Отлично! Так и запишем!
        {selectedEvent.name}
         <i>{selectedEvent.description}</i>
         \nНапишит одним сообщением, сколько билетов тебе нужно и на кого оформляешь. Например, <i>'1, Иванов Петр' или '2, Иванов Петр и Иванова Василина'</i>
         \n Если ошибся с выбором или хочешь узнать о других мероприятиях, кликни /start""",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(OrderStates.orderDetailsGetting)

    @router.message(AnyAttachmentFilter(), ChatTypeFilter("private"))
async def cmd_forward_attachment(message: Message, 
                                 bot: Bot, 
                                 internal_user_id: int):
    await message.reply(
        #TODO: здесь можно отдать список дополнительных комманд и что делать если билета долго нет. 
        text="""Спасибо! Передам вложение своим коллегам! Ожидайте билет в ближайшее время!
        Если хотите узнать о других мероприятиях и оформить другой билет, кликните /start 
        В случае возникновения проблем, долго ожидания билета или других вопросов - нажмите /help"""
    )
    requests = db.getTicketRequests()
    userRequests = filter(lambda x: x.user_id == internal_user_id and x.status !=1, requests)
    generateCommands = ""
    for userRequest in userRequests:
        event = db.getEvent(userRequest.event_id)
        generateCommands += f"\n{userRequest.requestTimeStamp}: {event.id}:'{event.name}', билеты для '{userRequest.requestDescription}'. Команда для генерации 1 билета: \n<b>%generateTicket {userRequest.id} 1</b>"
    request = ' '.join((
        f"Пользователь id:{internal_user_id} :@{message.from_user.username} отправил вложение.\n", 
        "Актуальные запросы пользователя:",
        f"{generateCommands}"))
    await resend_message_to_admin_group(message, bot, request)

