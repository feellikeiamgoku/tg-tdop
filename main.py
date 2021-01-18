import logging
import os

from telegram.ext import Updater, Filters, MessageHandler


from yt_bot.db import initializer
from yt_bot.core.handlers import ValidationHandler,pre_download_check, process_file


def setup():
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    token = os.getenv("BOT_TOKEN")
    initializer.run()

    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    link_handler = MessageHandler(Filters.text & (~Filters.command), pre_download_check)
    after_handler = ValidationHandler(process_file, run_async=True)
    dispatcher.add_handler(link_handler)
    dispatcher.add_handler(after_handler)
    updater.start_polling()


if __name__ == "__main__":
    setup()
