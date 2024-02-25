from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    notify = State() #прислать уведомление пользователям личным сообщением
    codeCheck = State() #проверка кодов в личном чате
