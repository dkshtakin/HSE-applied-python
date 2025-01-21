import logging
from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from handlers.common import back_reply_markup
from asyncio import Lock


logger = logging.getLogger(__name__)


users_lock = Lock()
users = {
}


class State(int, Enum):
    WEIGHT = 0,
    HEIGHT = 1,
    AGE = 2,
    ACTIVITY = 3,
    CITY = 4


async def update_user(user_id):
    async with users_lock:
        if user_id in users:
            return

        users[user_id] = {
            'weight': 0,
            'height': 0,
            'age': 0,
            'activity': 0,
            'city': '',
            'logged_water': 0,
            'logged_calories': 0,
            'water_goal': 0,
            'calories_goal': 0,
            'extra_water': 0,
            'burned_calories': 0,
            'last_food_calories': 0,
        }


async def set_user_info(user_id, key, value):
    await update_user(user_id)
    async with users_lock:
        users[user_id][key] = value


async def log_user_info(user_id, key, value):
    await update_user(user_id)
    async with users_lock:
        if key not in users[user_id]:
            users[user_id][key] = 0
        users[user_id][key] += value


async def set_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Введите ваш вес (в кг):",
            reply_markup=back_reply_markup('вес'),
        )
    else:
        await update.callback_query.message.reply_text(
            "Введите ваш вес (в кг):",
            reply_markup=back_reply_markup('вес'),
        )
    return State.WEIGHT


async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_weight = float(update.message.text)
    logger.info(f'User {user} set_weight {user_weight}')

    await set_user_info(user.id, 'weight', user_weight)

    await update.message.reply_text(
        "Введите ваш рост (в см):",
        reply_markup=back_reply_markup('рост'),
    )

    return State.HEIGHT


async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_height = float(update.message.text)
    logger.info(f'User {user} set_height {user_height}')

    await set_user_info(user.id, 'height', user_height)

    await update.message.reply_text(
        "Введите ваш возраст:",
        reply_markup=back_reply_markup('возраст'),
    )

    return State.AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_age = float(update.message.text)
    logger.info(f'User {user} set_weight {user_age}')

    await set_user_info(user.id, 'age', user_age)

    await update.message.reply_text(
        f'Сколько минут активности у вас в день?',
        reply_markup=back_reply_markup('активность'),
    )

    return State.ACTIVITY


async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_activity = float(update.message.text)
    logger.info(f'User {user} set_activity {user_activity}')

    await set_user_info(user.id, 'activity', user_activity)

    await update.message.reply_text(
        f'В каком городе вы находитесь?',
        reply_markup=back_reply_markup('город'),
    )

    return State.CITY


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_city = update.message.text
    logger.info(f'User {user} set_city {user_city}')

    await set_user_info(user.id, 'city', user_city)
    await set_user_info(user.id, 'completed', True)

    async with users_lock:
        user_data = users[user.id].copy()

    await update.message.reply_text(
        f'Отлично! Теперь команды из /menu покажут вам более подробную статистику с учетом введенных данных',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def invalid_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'Некорректный формат данных, введите вес (в кг):',
        reply_markup=back_reply_markup('вес'),
    )
    return State.WEIGHT


async def invalid_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'Некорректный формат данных, введите рост (в см):',
        reply_markup=back_reply_markup('рост'),
    )
    return State.HEIGHT


async def invalid_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'Некорректный формат данных, введите возраст:',
        reply_markup=back_reply_markup('возраст'),
    )
    return State.AGE


async def invalid_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'Некорректный формат данных, введите активность (в мин):',
        reply_markup=back_reply_markup('активность'),
    )
    return State.ACTIVITY


async def invalid_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'Некорректный формат данных, введите город:',
        reply_markup=back_reply_markup('город'),
    )
    return State.CITY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f'User {user} cancelled set_profile')
    await update.message.reply_text(
        'Вы всегда сможете настроить профиль пользователя позже при помощи команды /set_profile!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
