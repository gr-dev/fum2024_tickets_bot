import db
import datetime
#https://segno.readthedocs.io/en/latest/
import segno
import uuid
import os

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from db import Event

from db import ImageTicket
#работа с qr была организована по статье ниже
#https://realpython.com/python-generate-qr-code/

pathForGeneratedQr = "./misc/img/qr"
pathForTickets = "./misc/img/ticket"
baseImageForTickets = './misc/img/base/blue_petuh.jpg'
fontFile = "./misc/fonts/TIMES.ttf"

#TODO: переделать генератор в класс и при создании экземпляра передавть настройки может быть?



def generateTicket(event: Event)-> ImageTicket:
    __checkRequiredPaths()
    ticket = ImageTicket()
    ticket.ticketId = datetime.datetime.now().strftime("%Y-%m-%d %H %M %S")
    jsonTicket = ticket.toJson()
    qrcodeGenerator = segno.make_qr(jsonTicket)
    # для удаления белой рамки в следующий метод border=0,
    #    light="lightblue" или #ADD8E6 изменение цвета фона,
    #    перекрасить белую рамку quiet_zone="maroon",
    qrFileName = f"{pathForGeneratedQr}/{ticket.ticketId}.png"
    qrcodeGenerator.save(qrFileName, scale = 5)
    ticket.ticketFilePath = pasteQrOnBaseLayer(baseImageForTickets, qrFileName, f"{event.name}\n", event.description, ticket.ticketId, fontFile)
    return ticket

def pasteQrOnBaseLayer(baseLayer: str, pathToQr:str,  topic: str, body:str, ticketId: str, fontFilePath: str):
    baseLayer= Image.open(baseLayer)
    qrCodeImage = Image.open(pathToQr)
    ticketImage=baseLayer.copy()
    ticketImage.paste(qrCodeImage, (baseLayer.width - (int)(qrCodeImage.width/2) - (int(baseLayer.width/3/2)), baseLayer.height - qrCodeImage.height - 100))
    

    draw = ImageDraw.Draw(ticketImage)
    #TODO: для работы класса нужно наличие шрифта
    #https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.truetype
    font = ImageFont.truetype(fontFilePath, baseLayer.height / 20)
    draw.text((int(baseLayer.width / 10), int(baseLayer.height/9)), topic, fill = "#1f1e1e", font=font)
    
    font = ImageFont.truetype(fontFilePath, baseLayer.height / 25)
    draw.text((int(baseLayer.width / 10), int(baseLayer.height/6)), body, "#1f1e1e", font=font)
    resultFileName = f'{pathForTickets}/{ticketId}.jpg'
    ticketImage.save(resultFileName, quality = 95)
    baseLayer.close()
    qrCodeImage.close()
    return resultFileName

def __checkRequiredPaths():
    if not os.path.exists(pathForGeneratedQr):
        os.mkdir(pathForGeneratedQr)
    if not os.path.exists(pathForTickets):
        os.mkdir(pathForTickets)

if __name__ == "__main__":
    event = Event()
    event.id = 1
    event.name = "Чуб 2023"
    event.description = "Лучший Чуб в мире!"
    generateTicket(event)


