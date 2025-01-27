import gspread
from babel.dates import format_date, format_datetime, format_time
import config_reader

from db import CodeTicket

credentials = config_reader.config.GOOGLECREDENTIALS.get_secret_value()
workFile = config_reader.config.GOOGLESHEET.get_secret_value()

#https://docs.gspread.org/en/latest/index.html
def addCodeTicket(ticket: CodeTicket):
    sh = __getSpreadSheet()
    worksheet = sh.get_worksheet(0)
    values_list = worksheet.col_values(1)
    rowNumber = len(values_list)
    rowNumber+=1
    #TODO: контакт телеграмм добавить
    worksheet.update(f'A{rowNumber}:K{rowNumber}', [[ticket.id, 
                                                     ticket.code, 
                                                     ticket.event_id,
                                                     f"{ticket.event.name}, {format_datetime(ticket.event.eventDate, 'd MMM HH:mm', locale='ru_RU')}", 
                                                     ticket.contactInformation,
                                                     ticket.user_id, 
                                                     f"{ticket.user.name}",
                                                     ticket.cost, 
                                                     format_datetime(ticket.created, 'd MMM HH:mm', locale='ru_RU'), 
                                                     ticket.confirmationFileName,
                                                     ticket.confirmationFileId]])

def __getSpreadSheet():
    gc = gspread.service_account(filename=credentials)
    sh = gc.open(workFile)
    return sh