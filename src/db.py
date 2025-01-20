import datetime
import json
from typing import Dict, Any
#https://metanit.com/python/database/3.2.php
from sqlalchemy import create_engine, MetaData
from sqlalchemy import  Column, Integer, String, TIMESTAMP, TIME, Date, ForeignKey, Boolean, BIGINT, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy import select
from sqlalchemy.orm import lazyload

from aiogram.types import TelegramObject
from aiogram.types import  User as TelegramUser

from config_reader import config

engine = create_engine(config.connection_string.get_secret_value())#, echo=True для отображения запросов в выводе работы приложения

class Base(DeclarativeBase): pass
  
# создаем модель, объекты которой будут храниться в бд
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True) #id пользователя во внутренней базе данных
    name = Column(String)  
    telegramId = Column(BIGINT)
    ticketRequests = relationship("TicketRequest", back_populates="user")
    #tickets = relationship("Ticket", back_populates="user")

class PaymentInfo(Base):
    __tablename__ = "paymentInfos"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    additionalInfo = Column(String, nullable=True)
    eventGroups = relationship("EventGroup", back_populates="paymentInfo")

class UserRating(Base):
    __tablename__ = "userRatings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    value = Column(Integer) #оценка
    timestamp = Column(TIMESTAMP)

class TicketRequest(Base):
    __tablename__ = "ticketRequests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="ticketRequests", lazy= "joined")
    requestTimeStamp = Column(TIMESTAMP)
    event_id = mapped_column(Integer, ForeignKey("events.id"))
    event = relationship("Event", lazy= "joined")
    requestDescription = Column(String)
    cost = Column(Integer) #стоимость мероприятия на момент покупки билета
    status = Column(Integer, default=0) # 0 - новый, 1 - подтвержденный, 2 - (оплаченный), 3 - аннулированный ()

class EventGroup(Base):
    __tablename__ = "eventGroups"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    events = relationship("Event", back_populates="eventGroup", lazy="joined")
    hide = Column(Boolean, default = False)
    paymentInfo = relationship("PaymentInfo", back_populates="eventGroups", lazy="joined")
    paymentInfo_id = Column(Integer, ForeignKey("paymentInfos.id"), default=1)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    eventDate = Column(DateTime)
    description = Column(String)
    displayUntil = Column(DateTime)
    cost = Column(Integer)
    hide = Column(Boolean, default= False)
    eventGroupId = Column(Integer,  ForeignKey("eventGroups.id"), default=1,) #подразумеваю группировку событий по группам, например ФУМ или фестиваль
    eventGroup = relationship("EventGroup", back_populates="events", lazy="joined")
    #tickets = relationship("Ticket", back_populates="Event", lazy="joined")

class Ticket(Base):
    __tablename__ = "tickets"
    __abstract__=True
    id =  Column(Integer, primary_key=True, autoincrement=True)
    #user = relationship("User", back_populates="tickets")
    user = User()
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    #event = relationship("Event", back_populates="tickets")
    #костыль, так как иначе получаю исклюение, видимо из-за того, что абстрактный класс
    event = Event()
    created = Column(TIMESTAMP)
    checked = Column(Boolean, default=False)
    checkedTimestamp = Column(TIMESTAMP)
    confirmationFileId = Column(String)
    confirmationFileName = Column(String)
    confirmationType = Column(String)
    contactInformation = Column(String)
    cost = Column(Integer)

#билеты в виде картинки с QR
class ImageTicket(Ticket):
    __tablename__ = "imageTickets"
    ticketFilePath = Column(String)
    telegramFileId = Column(String)

#билеты с кодами
class CodeTicket(Ticket):
    __tablename__ = "codeTickets"
    code = Column(Integer)

class UpdateLog(Base):
    __tablename__ = "updateLogs"
    id = Column(Integer, primary_key=True, index=True)
    logTimeStamp = Column(TIMESTAMP)
    telegramTimeStamp = Column(TIMESTAMP)
    message = Column(String)
    telegramChatId = Column(BIGINT)
    update_type = Column(String)
    exceptionMessage = Column(String)

class UserState(Base):
    __tablename__ = "userStates"
    id = Column(Integer, primary_key=True)
    bot_id =  Column(BIGINT)
    chat_id = Column(BIGINT)
    telegram_user_id = Column(BIGINT) #имеется ввиду телеграм Айди
    thread_id =  Column(BIGINT, nullable=True)
    destiny = Column(String, default="default")
    timeStamp = Column(TIMESTAMP)
    state = Column(String)
    group = Column(String)

class FeatureToggle(Base):
    __tablename__ = "featureToggles"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False) 

class UserDataState(Base):
    __tablename__ = "userDataStates"
    id = Column(Integer, primary_key = True)
    telegram_user_id = Column(BIGINT, index=True)
    chat_id = Column(BIGINT)
    data = Column(JSON)
  
# создаем таблицы
#это использовал при sqlite
#Base.metadata.create_all(bind=engine)
 
#https://metanit.com/python/database/3.3.php

def addUpdateLog(update: UpdateLog) -> int:
    with Session(autoflush=False, bind=engine) as db:
        db.add(update)
        db.commit()
        return update.id
    
def switchFtStatus(ftId: int):
    with Session(autoflush=False, bind=engine, expire_on_commit=False) as db:
        ft = db.get(FeatureToggle, ftId)
        ft.enabled = not ft.enabled
        db.commit()
        return ft
    
def getFeatureToggles():
    with Session(autoflush=False, bind=engine) as db:
        ft = db.query(FeatureToggle).all()
        return ft

def hideEvent(eventId: int):
    with Session(autoflush=False, bind=engine, expire_on_commit=False) as db:
        event = db.get(Event, eventId )
        event.hide = True
        db.commit()
        return event      

#возвращает internal_id пользователя
def addTelegramUser(telegramUser: TelegramUser) -> int:
  with Session(autoflush=False, bind=engine) as db:
    first = db.query(User).filter(User.telegramId==telegramUser.id).first()
    if first != None:
        return first.id
    user = User(name=telegramUser.full_name)
    user.telegramId = telegramUser.id
    db.add(user)
    db.commit()
    return user.id

def addUserTicketRequest(event_id: int, internal_user_id: int, requestDescription: str | None = None) -> int:
    with Session(bind = engine) as db:
        event = db.query(Event).filter(Event.id == event_id).first()
        ticketRequest = TicketRequest()
        ticketRequest.event_id = event_id
        ticketRequest.user_id = internal_user_id
        ticketRequest.requestDescription = requestDescription
        ticketRequest.requestTimeStamp = datetime.datetime.now()
        ticketRequest.cost = event.cost
        db.add(ticketRequest)
        db.commit()
        return ticketRequest.id
    
def addCodeTicket(ticket: CodeTicket) -> int:
    with Session(bind=engine) as db:
        db.add(ticket)
        db.commit()
        return ticket.id
    

def getUsers() -> list[User]:
    with Session(autoflush=False, bind=engine) as db:
        people = db.query(User).all()
        return people

def getUserByInternalId(internal_user_id: Integer) -> User | None:
    with Session(bind=engine) as db:
        user = db.query(User).filter(User.id == internal_user_id).first()
        return user
    
def getEvent(event_id: Integer) -> Event | None:
    with Session(bind=engine) as db:
        event = db.get(Event, event_id)
        return event

def getEvents() -> list[Event]:
    with Session(bind=engine) as db:
        return db.query(Event).all()

def getEventGroups() -> list[EventGroup]:
    with Session(bind=engine) as db:
        result = db.query(EventGroup).join(Event).all()
        return result
    #with Session(bind=engine) as db:
    #    stmt = select(EventGroup).options(joinedload(EventGroup.events))
    #    return db.execute(stmt)

    
def getTicketRequests(includeAnnualRequests: bool = False):
    with Session(bind=engine) as db:
        #q = session.query(User).join(Address, User.id==Address.user_id)
        #db.query(Parent).options(joinedload(Parent.children)).all()
        #if not includeAnnualRequests:
        #    ticketRequests = db.query(TicketRequest).options(joinedload(TicketRequest.event)).filter(TicketRequest.status != 3).join(Event, TicketRequest.event_id == Event.id).all()
        #else:
        #    ticketRequests = db.query(TicketRequest).options(joinedload(TicketRequest.event)).join(Event, TicketRequest.event_id == Event.id).all()
        tRequests = db.query(TicketRequest).join(Event).all()
        
        if(includeAnnualRequests):
            return tRequests
        else:
            result =  filter(lambda x: x.status != 3, tRequests)
            return result

    
def getTicketRequest(ticketRequestId: int):
    with Session(bind=engine) as db:
        ticketRequest = db.query(TicketRequest).filter(TicketRequest.id == ticketRequestId).first()
        return ticketRequest

#проставить статус 2 у TicketRequest с переданными id
def completeTicketRequests(ids: list):
    with Session(bind=engine) as db:
        ticketRequest = db.query(TicketRequest).all()
        #я пытался отфильтровать на уровне запроса к базе, но у меня не получилось. А может в памяти делать это экономичней?
        for tr in ticketRequest:
            if tr.id in ids:
                tr.status = 2
        db.commit()

def examplefilter():
    with Session(autoflush=False, bind=engine) as db:
        people = db.query(User).filter(User.age > 30).all()
        for p in people:
            print(f"{p.id}.{p.name} ({p.age})")
        first = db.query(User).filter(User.id==1).first()
        print(f"{first.name} ({first.age})")

def getUserTickets(internalUserId: int):
    with Session(bind=engine) as db:
        userTickets = db.query(CodeTicket).filter(CodeTicket.user_id == internalUserId).all()
        return userTickets

def getCodeTickets():
    with Session(bind=engine) as db:
        tickets = db.query(CodeTicket).all()
        #TODO костыль на подключение связанной сущности
        events = db.query(Event).all()
        for t in tickets:
            t.event = next(filter(lambda x: x.id == t.event_id ,events))
        return tickets
    
def confirmUserRequests(user_id: int, orderDetails: str) ->None:
    with Session(autoflush=False, bind=engine) as db:
        ticketRequests = db.query(TicketRequest).filter(TicketRequest.user_id == user_id).filter(TicketRequest.status == 0).all()
        for r in ticketRequests:
            r.status = 1 #подтвержденный
            r.requestDescription = orderDetails
        db.commit()

def cancelUserticketRequestsExcludeCompleted(internalUser_id: int):
    with Session(autoflush=False, bind=engine) as db:
        statuses = [0, 1]
        ticketRequest = db.query(TicketRequest).filter(TicketRequest.user_id == internalUser_id ).filter(TicketRequest.status.in_(statuses)).all()
        if len(ticketRequest) == 0:
            return
        for c in ticketRequest:
            c.status = 3 #анулирован
        db.commit()

#работа с состоянием

def addUserState(state: UserState) -> int:
    with Session(bind=engine) as db:
        db.add(state)
        db.commit()
        return state.id

def getUserState(telegramUserId: int, chatId: int) -> UserState | None:
    with Session(autoflush=False, bind=engine) as db:
        result = db.execute(select(UserState).where(UserState.chat_id == chatId).where(UserState.telegram_user_id == telegramUserId).order_by(desc(UserState.id)))
        for state in result.scalars():
            return state
        return None
        #state = db.query(UserState).filter(UserState.telegram_user_id == telegramUserId and UserState.chat_id == chatId).order_by(desc(UserState.id)).first()
        return state
    
def setUserDataState(telegramUserId: int, chatId: int,  data: Dict[str, Any]) -> int:
    with Session(bind=engine) as db:
        userDataState = db.query(UserDataState).filter(UserDataState.telegram_user_id == telegramUserId and UserDataState.chat_id == chatId).order_by(desc(UserDataState.id)).first()
        if userDataState == None:  
            udata = UserDataState()
            udata.telegram_user_id = telegramUserId
            udata.chat_id = chatId
            udata.data = json.dumps(data, indent = 4)
            db.add(udata)
            db.commit()
            return udata.id 
        else:
            userDataState.data = json.dumps(data, indent = 4)
            db.commit()
            return userDataState.id
        
def getUserDataState(telegramUserId: int, chatId: int) -> None | Dict[str, Any]:
    with Session(autoflush=False, bind=engine) as db :
        userDataState = db.query(UserDataState).filter(UserDataState.telegram_user_id == telegramUserId and UserDataState.chat_id == chatId).order_by(desc(UserDataState.id)).first()
        if userDataState != None:
            return userDataState.data
        return None
    
def addUserRating(rating: UserRating):
    with Session(bind= engine) as db:
        db.add(rating)
        db.commit()
    
def updateUserDataState(telegramUserId: int, chatId: int, newData: Dict[str, Any]) -> Dict[str, Any]:
    with Session(autoflush=False, bind=engine) as db:
        userDataState = db.query(UserDataState).filter(UserDataState.telegram_user_id == telegramUserId and UserDataState.chat_id == chatId).order_by(desc(UserDataState.id)).first()
        if userDataState != None:        
            oldData = json.loads(userDataState.data)
            oldData.update(newData)
            userDataState.data = json.dumps(oldData, indent=4)
            db.commit()
            return userDataState.data
        else:
            setUserDataState(telegramUserId, chatId, newData)
            return newData
        
#Вспомогательный метод для разработки
def __initDb():
    with Session(autoflush=False, bind=engine) as db:
        evgroup1 = EventGroup()
        evgroup1.name = "мероприятия фестиваля "
        evgroup2 = EventGroup()
        evgroup2.name = "чуб 2024"
        db.add_all([ev1, ev2])
        db.commit()

        ev1 = Event( )
        ev1.name="ЧУБ 2024"
        ev1.description ="""Мероприятие года! Пройдет 20-21 апреля 2024 года, в Байкал Бизнес Центре. 
        32 игрока встретяться за столом переговоров, за два дня вы увидите совершенно разные ситуации и еще более невероятные исходы! Смех и серьезность идут тут плечом к плечу! 
        Стоимость Стандартного (Взрослого) билета на 1 день - стоимость 1200 руб., билет на 2 дня - 2200 руб. Для Студентов скидка - 1500руб. на оба дня. """
        #https://www.w3schools.com/python/python_datetime.asp
        ev1.eventDate = datetime.datetime(2024, 4, 20)
        ev1.paymentInfo = "Ссылка для оплаты Тинькофф: https://upload\.wikimedia\.org/wikipedia/ru/thumb/4/4d/Wojak\.png/200px\-Wojak\.png"
        ev1.eventGroupId = evgroup1.id
        ev2 = Event()
        ev2.name="Ныряние по технологии морских котиков"
        ev2.description = """Только 10 марта 2024 года! Смертельный номер - ныряние по технологии Котика! Без тренировок не повторять!"""
        ev2.eventDate = datetime.datetime(2024, 3, 10)
        ev2.paymentInfo = "Сбербанк, по номеру телефона `89642999999`"
        ev2.eventGroupId = evgroup1.id
        db.add_all([ev1, ev2])
        db.commit()

if __name__ == "__main__":
    __initDb()