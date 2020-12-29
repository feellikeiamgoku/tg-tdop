import os
import logging
from telegram.ext import Updater, Filters, MessageHandler, run_async
from telegram.bot import Bot

from tg_bot.download_youtube import download_mp3
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

BOT_TOKEN = os.getenv("BOT_TOKEN")


@run_async
def process_link(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Processing your video...")
    link = update.message.text
    with download_mp3(link) as downloaded:
        msg = context.bot.send_audio(chat_id=update.effective_chat.id,
                               audio=open(downloaded, 'rb'), timeout=1000)
        if msg:
            print(msg)
        else:
            print("got error while parsing msg")


if __name__ == "__main__":
    bot = Bot(BOT_TOKEN)
    updater = Updater(bot=bot)
    dispatcher = updater.dispatcher
    link_handler = MessageHandler(Filters.text & (~Filters.command), process_link)
    dispatcher.add_handler(link_handler)
    updater.start_polling()
