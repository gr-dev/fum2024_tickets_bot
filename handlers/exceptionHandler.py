from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types.error_event import ErrorEvent

from filters.any_attachment import AnyAttachmentFilter
from filters.group_id import GroupIdFilter

from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

router = Router()

@router.error(F.update.message.as_("message"))
async def cmd_help_message_if_exception(event: ErrorEvent,
                                        message: Message,
                                        state: FSMContext):
    answer = """Похоже я не смог корректно обработать твой запрос. 
    Я постоянно меняюсь и возможно для продолжения работы нужны новые данные
    Пожалуйста, оформи заказ сначала, нажав /start 
    Если проблема возникнет повторно, пожалуйста, свяжись с @Romkin или по номеру +79501011198"""
    await message.reply(
        text=answer)
    await state.clear()
