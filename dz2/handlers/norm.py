import logging
from enum import Enum
from handlers.set_profile import users, users_lock, set_user_info
from api.weather import get_current_temperature
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler


logger = logging.getLogger(__name__)


async def update_water_goal(user_id):
    async with users_lock:
        if user_id not in users or 'completed' not in users[user_id]:
            return None
        user_data = users[user_id]

    user_norm_water = user_data['weight'] * 30 + (user_data['activity'] / 30) * 500

    temperature = await get_current_temperature(user_data['city'])
    if temperature is not None:
        user_norm_water += 500 * (temperature > 25)

    await set_user_info(user_id, 'water_goal', user_norm_water)
    return user_norm_water


async def update_calories_goal(user_id):
    async with users_lock:
        if user_id not in users or 'completed' not in users[user_id]:
            return None
        user_data = users[user_id]

    user_norm_calories = user_data['weight'] * 10 + user_data['height'] * 6.25 - \
    user_data['age'] * 5 + (user_data['activity'] / 60) * 150

    await set_user_info(user_id, 'calories_goal', user_norm_calories)
    return user_norm_calories


async def norm_water(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user = update.message.from_user
    else:
        user = update.callback_query.from_user

    async with users_lock:
        if user.id not in users or 'completed' not in users[user.id]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Профиль пользователя не полный, задайте его при помощи комманды /set_profile!'
            )
            return

    user_norm_water = await update_water_goal(user.id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'💧 Ваша дневная норма воды: {user_norm_water} мл'
    )


async def norm_calories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user = update.message.from_user
    else:
        user = update.callback_query.from_user

    async with users_lock:
        if user.id not in users or 'completed' not in users[user.id]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Профиль пользователя не полный, задайте его при помощи комманды /set_profile!'
            )
            return

    user_norm_calories = await update_calories_goal(user.id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'🍽️ Ваша дневная норма калорий: {user_norm_calories} ккал'
    )
