import asyncio
import logging
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import config
from handlers import exceptionHandler, commonHandler, adminHandler, developHandler, partnerHandler, rootHandler
from alembic.config import Config
from alembic import command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from babel.dates import format_date, format_datetime, format_time
from datetime import datetime

from middlewares import commonMiddleware
from middlewares import commonServicesMiddleware
import pgStorage
from config_reader import config
from services import featureToggleService, notificationService

def register_all_middlewares(dp:Dispatcher, scheduler: AsyncIOScheduler, bot: Bot):
    #middleware that log events, insert internal_user_id
    dp.update.outer_middleware(commonMiddleware.CommonMiddleware())
    ftService = featureToggleService.FeatureToggleService()
    #регистрация на все обновления
    notificationServ = notificationService.NotificationService(scheduler, bot)
    dp.update.middleware.register(commonServicesMiddleware.CommonServicesMiddleware(notificationServ, ftService))
 
def register_all_handlers(dp:Dispatcher):
    if config.ENVIRONMENT.get_secret_value() == "development":
        dp.include_router(developHandler.router)
    dp.include_router(adminHandler.router)
    dp.include_router(rootHandler.router)
    dp.include_router(partnerHandler.router)
    dp.include_router(commonHandler.router)
    dp.include_router(exceptionHandler.router)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=pgStorage.PgStorage())
    sheduler = AsyncIOScheduler(timezone="Asia/Irkutsk")
    register_all_middlewares(dp, sheduler, bot)
    register_all_handlers(dp)
    try:
        sheduler.start()
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        await bot.send_message(chat_id=config.admin_group.get_secret_value(), text=f" {date} Бот запущен.")
        await dp.start_polling(bot)
    finally:
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        await bot.send_message(chat_id=config.admin_group.get_secret_value(), text= f"{date} Завершение работы бота")
        

if __name__ == "__main__":
    asyncio.run(main())