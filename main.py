import os
import logging
from telegram.ext import Updater, Filters, MessageHandler, run_async
from telegram.bot import Bot

from yt_bot.core.pre_processing import get_further_processing, check_processed
from yt_bot.core.processing import process
from yt_bot.core.post_processing import save_processed
from yt_bot.db.initialize import Initializer
from yt_bot.yt.context import DirContext
from youtube_dl import DownloadError


@run_async
def process_link(update, context):
    message = update.message.text
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id

    future, msg = get_further_processing(message)
    context.bot.send_message(chat_id, msg)

    if future:
        processed = check_processed(future.video_id)
        if processed:
            processed_chat, processed_msg = processed[0], processed[1]
            context.bot.forward_message(chat_id, processed_chat, processed_msg)
        else:
            try:
                with DirContext(chat_id, message_id):
                    path = process(future.link)
                    msg = context.bot.send_audio(chat_id, open(path, 'rb'), timeout=1000)
            except DownloadError:
                context.bot.send_message(chat_id, "Error with link")
            else:
                save_processed(chat_id, msg.message_id, future.video_id, future.link)


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
