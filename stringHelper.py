from enum import Enum

class MessageType(Enum):
    HellowMessage = 1
    SelectingEvent = 2
    GetUserInfo = 3
    AwaitingPaymentMessage = 4
    ConfirmationMessage = 5
    Test = 6

class CommonHandlerStringHelper():

    def __init__(self) -> None:
        self.hellowMessage = """Добро пожаловать! Через данный бот можно оформить билеты на отдельные мероприятия КСТ. Выбери один из пукнтов меню ниже"""
        self.confirmationMessage = """Билеты на мероприятия куплены. Ниже указаны коды каждого билета. Сохрани это сообщение.
При регистрации на самом мероприятии назови администратору на ресепшене соответствующий код и имя, на которое был оформлен заказ."""
        self.getDetails = """Пожалуйста, укажи свои контакты: ФИО и номер телефона для связи. Например, 'Седых Виктория Георгиевна, 89648888456'"""
        self.selectingEventMessage = """Отметь мероприятия, которые хотел бы посетить:"""
        self.awaitingPayment = """Сделай перевод c помощью СБП по номеру [\+79149279685](tel:\+79149279685) на *Тинькофф Банк* \(получатель Кирилл Х\.\) и отправь *в данный чат* чек/квитанцию"""
        self.test = """[ссылке Тинькофф](https://www\.tinkoff\.ru/cf/Aa6jwmGYajX) привет"""

    def GetText(self, level: MessageType) -> str:
        if level == MessageType.HellowMessage:
            return self.hellowMessage
        elif level == MessageType.ConfirmationMessage:
            return self.confirmationMessage
        elif level == MessageType.SelectingEvent:
            return self.selectingEventMessage
        elif level == MessageType.GetUserInfo:
            return self.getDetails
        elif level == MessageType.AwaitingPaymentMessage:
            return self.awaitingPayment
        elif level == MessageType.Test:
            return self.test
        
