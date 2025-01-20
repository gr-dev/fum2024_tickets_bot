from aiogram.fsm.state import StatesGroup, State

class PartnerStates(StatesGroup):
    contributionType = State() #тип вклада, анонимный или публичный
    contactInformation = State() #получение инфо
    contributionSize = State()#Размер вклада
    gettingConfirmation = State() #получение подтверждения
    completed = State() #вклад совершен
