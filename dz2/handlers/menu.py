import logging
from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler


from handlers.set_profile import set_profile, State
from handlers.norm import norm_water, norm_calories
from handlers.progress import check_progress
from handlers.common import back_reply_markup


class MenuKeyboard(str, Enum):
    SET_PROFILE = '/set_profile',
    NORM_WATER = '/norm_water',
    NORM_CALORIES = '/norm_calories',
    CHECK_PROGRESS = '/check_progress'


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button1 = InlineKeyboardButton(
        f'🙍🏻‍♂️ Настройка профиля',
        callback_data=MenuKeyboard.SET_PROFILE.value
    )
    button2 = InlineKeyboardButton(
        f'📈 Текущий прогресс',
        callback_data=MenuKeyboard.CHECK_PROGRESS.value
    )
    button3 = InlineKeyboardButton(
        f'💧 Дневная норма воды',
        callback_data=MenuKeyboard.NORM_WATER.value
    )
    button4 = InlineKeyboardButton(
        f'🍽️ Дневная норма калорий',
        callback_data=MenuKeyboard.NORM_CALORIES.value
    )

    keyboard = [[button1, button2], [button3, button4]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    menu_text = f'📋 Menu\n\n'\
                f'Доступные команды:\n'\
                f' - /set_profile - настройка профиля пользователя\n'\
                f' - /check_progress - отобразить текущий прогресс\n'\
                f' - /norm_water - дневная норма воды\n'\
                f' - /norm_calories - дневная норма калорий\n'\
                f' - /log_water <количество выпитой воды (в мл)> - сохраняет сколько воды выпито'\
                f' и показывает сколько осталось до нормы\n'\
                f' - /log_food <название продукта> - сохраняет калорийность\n'\
                f' - /log_workout <тип тренировки> <время (мин)> - фиксирует сожжённые калории и'\
                f' учитывает расход воды на тренировке\n'

    await update.message.reply_text(
        menu_text,
        reply_markup=reply_markup
    )


async def menu_button_callback(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    button = query.data

    logging.info(f'pressed {button}')

    await query.answer()

    if button == MenuKeyboard.SET_PROFILE.value:
        await update.callback_query.message.reply_text(
            "Введите ваш вес (в кг):",
            reply_markup=back_reply_markup('вес'),
        )
        context.user_data['conversation_active'] = True
        return State.WEIGHT
    elif button == MenuKeyboard.CHECK_PROGRESS.value:
        await check_progress(update, context)
    elif button == MenuKeyboard.NORM_WATER.value:
        await norm_water(update, context)
    elif button == MenuKeyboard.NORM_CALORIES.value:
        await norm_calories(update, context)
    else:
        await query.edit_message_text(
            text=f"Простите, но я не понимаю данную команду"
        )
