from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    help = State() #запрос помощи
    eventGroupSelection = State() #выбор группы мероприятий
    eventSelection = State() #выбор мероприятия
    orderDetailsGetting = State() #сколько билетов, кому - заполнение информации
    orderConfirmation = State() #подтверждение заполненной информации
    paymentAwaiting = State() #ожидание оплаты
    completedOrder = State() #человек заполнил информацию и заплатил, ожидает билеты