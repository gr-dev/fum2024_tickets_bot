from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
import db
from db import UpdateLog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from services import featureToggleService, notificationService
    
#https://botfather.dev/blog/zapusk-funkczij-v-bote-po-tajmeru#integration
class CommonServicesMiddleware(BaseMiddleware):
    def __init__(self, 
                 notificationService: notificationService.NotificationService, 
                 ftService: featureToggleService.FeatureToggleService):
        self.notificationService = notificationService
        self.ftService = ftService
        #super().__init__()
    
    async def __call__(self, 
                       handler: Callable[[TelegramObject, 
                                          Dict[str, Any]], 
                                          Awaitable[Any]], 
                        event: TelegramObject, 
                        data: Dict[str, Any]
                        ) -> Any:
        data['notificationService'] = self.notificationService
        data['ftService'] = self.ftService
        return await handler(event, data)
        #return await super().__call__(handler, event, data)