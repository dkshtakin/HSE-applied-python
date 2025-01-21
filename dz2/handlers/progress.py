import logging
from enum import Enum
from handlers.set_profile import users, users_lock
from handlers.set_profile import set_user_info, log_user_info, update_user
from handlers.norm import update_water_goal, update_calories_goal
from handlers.filters import float_pattern, int_pattern, char_pattern
from handlers.common import back_reply_markup
from api.food import get_food_info
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
import re


logger = logging.getLogger(__name__)


class State(int, Enum):
    GRAMS = 0,


async def log_water(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if not context.args or not (re.match(int_pattern, context.args[0]) or re.match(float_pattern, context.args[0])):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Некорректный формат данных, используйте /log_water <количество выпитой воды (в мл)>',
        )
        return

    user_water = float(context.args[0])
    await log_user_info(user.id, 'logged_water', user_water)

    async with users_lock:
        user_data = users[user.id].copy()

    user_water_current = users[user.id]['logged_water']
    if 'completed' in users[user.id]:
        user_water_goal = await update_water_goal(user.id) + users[user.id]['extra_water']
        response_text = f'💦 Зачтено {user_water} мл, всего {user_water_current} / {user_water_goal} мл'
        if user_water_current >= user_water_goal:
            response_text += f'\n✅  Дневная норма воды выполнена!'
        else:
            response_text += f'\n🔜  До нормы {user_water_goal - user_water_current} мл'
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response_text,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'💦 Зачтено {user_water} мл, всего {user_water_current} мл'\
                 f'⚠️ Для отслеживания нормы заполните профиль пользователя при помощи команды /set_profile!',
        )


async def log_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Некорректный формат данных, используйте /log_food <название продукта>',
        )
        return

    user_food = await get_food_info(context.args[0])
    if user_food is None or user_food['name'] is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'⚠️ Не удалось определить калорийность продукта "{context.args[0]}"',
        )
        return ConversationHandler.END

    calories = float(user_food['calories'])
    async with users_lock:
        users[user.id]['last_food_calories'] = calories

    await update.message.reply_text(
        f'🍌 {user_food["name"]} — {calories} ккал на 100 г. Сколько грамм вы съели?',
        reply_markup=back_reply_markup('вес'),
    )

    return State.GRAMS


async def log_food_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    async with users_lock:
        user_calories = (float(update.message.text) / 100) * users[user.id]['last_food_calories']

    await log_user_info(user.id, 'logged_calories', user_calories)

    async with users_lock:
        user_data = users[user.id].copy()

    user_calories_current = users[user.id]['logged_calories']
    if 'completed' in users[user.id]:
        user_calories_goal = await update_calories_goal(user.id)
        response_text = f'🍴 Зачтено {user_calories} ккал, всего {user_calories_current} / {user_calories_goal} ккал'
        if user_calories_current >= user_calories_goal:
            response_text += f'\n✅  Дневная норма калорий выполнена!'
        else:
            response_text += f'\n🔜  До нормы {user_calories_goal - user_calories_current} ккал'
        await update.message.reply_text(
            response_text,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            f'🍴 Зачтено {user_calories} ккал, всего {user_calories_current} ккал\n'\
                 f'⚠️ Для отслеживания нормы заполните профиль пользователя при помощи команды /set_profile!',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def invalid_grams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'Некорректный формат данных, введите вес (в граммах):',
        reply_markup=back_reply_markup('вес'),
    )
    return State.GRAMS


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user = update.message.from_user
    # await update.message.reply_text(
    #     'Вы всегда сможете настроить профиль пользователя позже при помощи команды /set_profile!',
    #     reply_markup=ReplyKeyboardRemove()
    # )
    return ConversationHandler.END


async def log_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if len(context.args) != 2 or not (re.match(int_pattern, context.args[1]) or re.match(float_pattern, context.args[1])):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Некорректный формат данных, используйте /log_workout <тип тренировки> <время (мин)>',
        )
        return

    train_type, train_time = context.args
    train_time = float(train_time)

    user_burned_calories = train_time * 10
    user_extra_water = (train_time / 30) * 200

    await log_user_info(user.id, 'burned_calories', user_burned_calories)
    await log_user_info(user.id, 'extra_water', user_extra_water)

    async with users_lock:
        user_data = users[user.id].copy()

    user_calories_current = users[user.id]['logged_calories']

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'🏃‍♂️ {train_type} {train_time} минут — {user_burned_calories} ккал. '\
             f'Дополнительно: выпейте {user_extra_water} мл воды.',
    )


async def check_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user = update.message.from_user
    else:
        user = update.callback_query.from_user

    await update_user(user.id)
    await update_water_goal(user.id)
    await update_calories_goal(user.id)

    async with users_lock:
        user_data = users[user.id].copy()

    completed = False
    if 'completed' in user_data:
        completed = True

    response_text = f'📊 Прогресс:\n\n'\
                    f'💦 Вода:\n'\
                    f' - Выпито: {user_data["logged_water"]} мл'
    if completed:
        response_text += f' из {user_data["water_goal"] + user_data["extra_water"]} мл'
    response_text += '\n'
    if completed:
        water_diff = user_data["water_goal"] + user_data["extra_water"] - user_data["logged_water"]
        if water_diff > 0:
            response_text += f' - Осталось: {water_diff} мл\n'
        else:
            response_text += f' - ✅  Дневная норма воды выполнена!\n'

    response_text += \
                    f'\n'\
                    f'🍴 Калории:\n'\
                    f'- Потреблено: {user_data["logged_calories"]} ккал'
    if completed:
        response_text += f' из {user_data["calories_goal"]} ккал'
    response_text += '\n'
    response_text += \
                    f'- Сожжено: {user_data["burned_calories"]} ккал\n'\
                    f'- Баланс: {user_data["logged_calories"] - user_data["burned_calories"]} ккал\n'

    if not completed:
        response_text += f'\n⚠️ Для отслеживания нормы заполните профиль пользователя при помощи команды /set_profile!'

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text,
    )
