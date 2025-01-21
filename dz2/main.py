import os
import asyncio
import logging
from handlers.filters import cancel_filter, number_filter, char_filter, back_filter
import handlers.common as common
import handlers.set_profile as set_profile
import handlers.norm as norm
import handlers.progress as progress
import handlers.menu as menu
import handlers.base as base
from telegram.ext import CommandHandler, MessageHandler, InlineQueryHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram.ext import filters, ApplicationBuilder
from dotenv import load_dotenv


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    print(TOKEN)

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', base.start)
    menu_handler = CommandHandler('menu', menu.menu)
    menu_button_callback_handler = CallbackQueryHandler(menu.menu_button_callback)

    set_profile_handler = CommandHandler('set_profile', set_profile.set_profile)
    set_profile_conv_handler = ConversationHandler(
        entry_points=[set_profile_handler, menu_button_callback_handler],
        states={
            set_profile.State.WEIGHT: [
                MessageHandler(number_filter, set_profile.weight),
                MessageHandler(back_filter, set_profile.cancel),
                MessageHandler(~ cancel_filter, set_profile.invalid_weight)
            ],
            set_profile.State.HEIGHT: [
                MessageHandler(number_filter, set_profile.height),
                MessageHandler(back_filter, set_profile.cancel),
                MessageHandler(~ cancel_filter, set_profile.invalid_height)
            ],
            set_profile.State.AGE: [
                MessageHandler(number_filter, set_profile.age),
                MessageHandler(back_filter, set_profile.cancel),
                MessageHandler(~ cancel_filter, set_profile.invalid_age)
            ],
            set_profile.State.ACTIVITY: [
                MessageHandler(number_filter, set_profile.activity),
                MessageHandler(back_filter, set_profile.cancel),
                MessageHandler(~ cancel_filter, set_profile.invalid_activity)
            ],
            set_profile.State.CITY: [
                MessageHandler(char_filter, set_profile.city),
                MessageHandler(back_filter, set_profile.cancel),
                MessageHandler(~ cancel_filter, set_profile.invalid_city)
            ],
        },
        fallbacks=[CommandHandler("cancel", set_profile.cancel)],
    )

    log_food_handler = CommandHandler('log_food', progress.log_food)
    log_food_conv_handler = ConversationHandler(
        entry_points=[log_food_handler],
        states={
            progress.State.GRAMS: [
                MessageHandler(number_filter, progress.log_food_answer),
                MessageHandler(back_filter, progress.cancel),
                MessageHandler(~ cancel_filter, progress.invalid_grams)
            ],
        },
        fallbacks=[CommandHandler("cancel", progress.cancel)],
    )

    norm_water_handler = CommandHandler('norm_water', norm.norm_water)
    norm_calories_handler = CommandHandler('norm_calories', norm.norm_calories)
    log_water_handler = CommandHandler('log_water', progress.log_water)
    log_food_handler = CommandHandler('log_food', progress.log_food)
    log_workout_handler = CommandHandler('log_workout', progress.log_workout)
    check_progress_handler = CommandHandler('check_progress', progress.check_progress)
    unknown_handler = MessageHandler(filters.COMMAND, base.unknown)

    application.add_handler(set_profile_conv_handler)
    application.add_handler(log_food_conv_handler)
    application.add_handler(start_handler)
    application.add_handler(menu_handler)
    application.add_handler(menu_button_callback_handler)
    application.add_handler(norm_water_handler)
    application.add_handler(norm_calories_handler)
    application.add_handler(log_water_handler)
    application.add_handler(log_workout_handler)
    application.add_handler(check_progress_handler)
    application.add_handler(unknown_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
