import logging
import os

from telegram.bot import Bot
from telegram.ext import Updater, Filters, MessageHandler, run_async

from yt_bot.core.exceptions import UserInputError, UserLimitError
from yt_bot.core.processing import Download
from yt_bot.db import initializer


@run_async
def process_link(update, context):
    message = update.message.text
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    bot = context.bot
    processor = Download(chat_id, message_id, message, bot)

    try:
        processor.run()
    except (UserInputError, UserLimitError) as e:
        processor.notify(e.msg)
    except Exception as e:
        logging.error(e)
        processor.notify('Something bad happen, please, try again later.')


def setup():
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    token = os.getenv("BOT_TOKEN")
    initializer.run()

    bot = Bot(token)
    updater = Updater(bot=bot)
    dispatcher = updater.dispatcher
    link_handler = MessageHandler(Filters.text & (~Filters.command), process_link)
    dispatcher.add_handler(link_handler)
    updater.start_polling()


if __name__ == "__main__":
    setup()