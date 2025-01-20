from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_row_keyboard(items: list[str], input_hint: str = "Выберите одно из значений") -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True, input_field_placeholder = input_hint)


def make_vertical_keyboard(items: list[str], input_hint: str = "Выберите одно из значений") -> ReplyKeyboardMarkup:
    replyKeyboard = ReplyKeyboardBuilder()
    for item in items:
        replyKeyboard.row(KeyboardButton(text = item))
    return replyKeyboard