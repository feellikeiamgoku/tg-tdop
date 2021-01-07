import os
import logging
from telegram.ext import Updater, Filters, MessageHandler, run_async
from telegram.bot import Bot

from yt_bot.core.pre_processing import get_definition, check_processed
from yt_bot.core.processing import process
from yt_bot.core.post_processing import save_processed

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

BOT_TOKEN = os.getenv("BOT_TOKEN")


@run_async
def process_link(update, context):
    message = update.message.text
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    definition = get_definition(message, context.bot, chat_id)


    pending = check_processed(bot, chat_id, *definition)
    to_save = process(chat_id, message_id, bot, *pending)
    save_processed(to_save)


if __name__ == "__main__":
    bot = Bot(BOT_TOKEN)
    updater = Updater(bot=bot)
    dispatcher = updater.dispatcher
    link_handler = MessageHandler(Filters.text & (~Filters.command), process_link)
    dispatcher.add_handler(link_handler)
    updater.start_polling()
