import logging
import os

from telegram.ext import Updater, Filters, MessageHandler


from yt_bot.db import initializer
from yt_bot.core.handlers import AudioHandler, ForwardUpdate, AudioUpdate
from yt_bot.core.callbacks import process_file, pre_download_check, forward


def setup():
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    token = os.getenv("BOT_TOKEN")
    initializer.run()

    updater = Updater(token=token, workers=8)
    dispatcher = updater.dispatcher
    check_handler = MessageHandler(Filters.text & (~Filters.command), pre_download_check)
    process_handler = AudioHandler(AudioUpdate, process_file, run_async=True)
    forward_handler = AudioHandler(ForwardUpdate, forward, run_async=True)
    dispatcher.add_handler(check_handler)
    dispatcher.add_handler(process_handler)
    dispatcher.add_handler(forward_handler)
    updater.start_polling()


if __name__ == "__main__":
    setup()
