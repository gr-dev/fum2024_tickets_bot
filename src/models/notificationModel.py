from models.enum_notificationType import NotificationType

class notificationModel:
    def __init__(self, notificationDate, message, chat_id, notificationType: NotificationType):
        #дата уведомления
        self.notificationDate = notificationDate
        self.message = message
        self.chat_id = chat_id
        #было ли выполнено уведомлене
        self.isCompleted = False
        #тип уведомления. Например, напоминание о высылке скриншота или напоминание о мероприятии
        self.notificationType = notificationType