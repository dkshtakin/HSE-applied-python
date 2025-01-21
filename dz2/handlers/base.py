import logging
from telegram import Update
from telegram.ext import ContextTypes
from handlers.set_profile import update_user


logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update_user(user.id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Отправь /menu для просмотра списка доступных команд!"
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Простите, но я не понимаю данную команду"
    )
