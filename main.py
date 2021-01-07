import os
import logging
from telegram.ext import Updater, Filters, MessageHandler, run_async
from telegram.bot import Bot

from yt_bot.core.pre_processing import get_definition, check_processed
from yt_bot.validation.definition import YTPlaylist

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

BOT_TOKEN = os.getenv("BOT_TOKEN")


# @run_async
def process_link(update, context):
    message = update.message.text
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    definition = get_definition(message, context.bot, chat_id)

    if isinstance(definition, YTPlaylist):
        definition = definition.get_links()
        if not definition:
            context.bot.send_message(chat_id=chat_id,
                                     text="Hey, you send me empty playlist, can't get anything from it")
            return
    else:
        definition = (definition,)

    pending = check_processed(bot, chat_id, *definition)

    # print(pending)


if __name__ == "__main__":
    bot = Bot(BOT_TOKEN)
    updater = Updater(bot=bot)
    dispatcher = updater.dispatcher
    link_handler = MessageHandler(Filters.text & (~Filters.command), process_link)
    dispatcher.add_handler(link_handler)
    updater.start_polling()
