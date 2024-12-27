import enum

class NotificationType(enum.Enum):
    #напоминание об отправке подтверждения
    sendConfirmation = 1
    #уведомление о близости мероприятия
    eventSoon = 2