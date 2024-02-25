import random
import db
class CodeTicketGenerator():
    #возвращает уникальный код для данного мероприятия
    def generateCodeTicket(eventId: int) -> int:
        tickets = db.getCodeTickets()
        start = 1000
        stop = 9999
        while True:
            code = random.randrange(start, stop)
            result  = next((x for x in tickets if x.code == code), 0)
            if result == 0 :
                break
        return code