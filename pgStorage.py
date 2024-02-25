from abc import ABC, abstractmethod
import datetime
from typing import Any, AsyncGenerator, Dict, Optional, Union

from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.fsm.state import State

import json

from db import UserState
import db

StateType = Optional[Union[str, State]]


class PgStorage(BaseStorage):
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
      userState = UserState()
      userState.bot_id = key.bot_id
      userState.telegram_user_id = key.user_id
      userState.chat_id = key.chat_id
      userState.destiny = key.destiny
      userState.thread_id = key.thread_id
      userState.timeStamp = datetime.datetime.now()
      if state is not None:
        userState.state = state.state
        #userState.group = state.group
      
      db.addUserState(userState)

    async def get_state(self, key: StorageKey) -> str | None:
       userState =  db.getUserState(key.user_id, key.chat_id)
       if (userState == None):
          return None
       return userState.state

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
       db.setUserDataState(key.user_id, key.chat_id, data )

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
       data = db.getUserDataState(key.user_id, key.chat_id)
       return json.loads(data)

    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
       data = db.updateUserDataState(key.user_id, key.chat_id, data)
       return data

    async def close(self) -> None:
       pass