import xlsxwriter
from xlsxwriter.worksheet import Worksheet
import datetime, os
import db

#https://xlsxwriter.readthedocs.io/example_datetimes.html

base_path = "misc/xlsx/"

#возвращает filename созданного файла
def createXlsxForTickets(fileName: str, codeTickets: list, infoText: str = None) ->str:
    os.makedirs(base_path, exist_ok=True)

    fileName = f"{base_path}{fileName}.xlsx"
    workbook = xlsxwriter.Workbook(fileName)
    worksheet = workbook.add_worksheet()
    worksheet.set_column("B:B",20)
    worksheet.set_column("C:C",30)
    #TODO: добавить информацию о мероприятии первой строкой, и дату формирования отчета
    if infoText != None:
        row = 1
        col = 5
        worksheet.insert_textbox(row, col, infoText)    
    _setHeaders(worksheet, ["code", "дата покупки", "контактная информация", "стоимость"])
    rowNumber = 1
    for ticket in codeTickets:
        rowNumber+=1
        worksheet.write(f"A{rowNumber}", ticket.code)
        worksheet.write(f"B{rowNumber}", ticket.created.strftime('%d %b, %H:%M'))
        worksheet.write(f"C{rowNumber}", ticket.contactInformation)
        worksheet.write(f"D{rowNumber}", ticket.cost)
    workbook.close()
    return fileName

def _setHeaders(worksheet: Worksheet, headers: list):
    column = 0
    for header in headers:
        worksheet.write(0, column, header)
        column+=1
    worksheet

if __name__ == "__main__":
    currentDate = datetime.datetime.now().strftime('%H %M')
    createXlsxForTickets(currentDate, db.getCodeTickets())