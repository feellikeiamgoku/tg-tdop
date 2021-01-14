import os
import logging
from telegram.ext import Updater, Filters, MessageHandler, run_async
from telegram.bot import Bot

from yt_bot.core.processing import DownloadProcessor, UserInputError
from yt_bot.db.initialize import Initializer


@run_async
def process_link(update, context):
    message = update.message.text
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    bot = context.bot
    processor = DownloadProcessor(chat_id, message_id, message, bot)

    try:
        processor.run()
    except UserInputError as e:
        processor.notify(e.msg)


def setup():
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    token = os.getenv("BOT_TOKEN")
    Initializer.run()

    bot = Bot(token)
    updater = Updater(bot=bot)
    dispatcher = updater.dispatcher
    link_handler = MessageHandler(Filters.text & (~Filters.command), process_link)
    dispatcher.add_handler(link_handler)
    updater.start_polling()


if __name__ == "__main__":
    setup()
