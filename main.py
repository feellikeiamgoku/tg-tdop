import os
import logging
from telegram.ext import Updater, Filters, MessageHandler, run_async
from telegram.bot import Bot

from yt_bot.core.pre_processing import get_definition, check_processed
from yt_bot.core.processing import process
from yt_bot.core.post_processing import save_processed
from yt_bot.db.initialize import Initializer
from utils import emoji


@run_async
def process_link(update, context):
    message = update.message.text
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id

    to_process, msg = get_definition(message)
    context.bot.send_message(chat_id, msg)

    if to_process:
        for processed_chat, processed_msg in check_processed(to_process):
            context.bot.forward_message(chat_id, processed_chat, processed_msg)

        for audio in process(chat_id, message_id, to_process):
            msg = context.bot.send_audio(chat_id, open(audio.path, 'rb'), performer=audio.author,
                                         title=audio.title, timeout=1000)
            audio.set_postprocess_values(chat_id, msg.message_id)
            save_processed(audio)


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
