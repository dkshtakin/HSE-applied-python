from enum import Enum
from telegram import ReplyKeyboardMarkup


class Keyboard(str, Enum):
    BACK = '🔙Назад',


def back_reply_markup(input_field_placeholder):
    back_reply_keyboard = [[Keyboard.BACK]]
    back_reply_markup = ReplyKeyboardMarkup(
        back_reply_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="вес"
    )
    return back_reply_markup
