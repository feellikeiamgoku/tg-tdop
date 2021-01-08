from typing import List

from youtube_dl import DownloadError
from telegram.bot import Bot

from utils import emoji
from yt_bot.validation.definition import DefineYTLinkType, Audio, EmptyPlayListError
from yt_bot.db.store import Store


def get_definition(message: str, bot: Bot, chat_id: int) -> List[Audio]:
    bot.send_message(chat_id=chat_id, text=f'Doing magic, wait a sec... {emoji.rainbow}')

    try:
        definer = DefineYTLinkType(message)
        to_process = definer.define()
    except DownloadError:
        bot.send_message(chat_id=chat_id,
                         text=f'Invalid link, please, take a look at provided link {emoji.exclamation_mark}')
    except EmptyPlayListError as e:
        bot.send_message(chat_id=chat_id, text=f'{e.msg} {emoji.exclamation_question_mark_selector}')
    else:
        bot.send_message(chat_id=chat_id, text=f'Processing your video... {emoji.robot}')
        return to_process


def check_processed(bot: 'Bot', chat_id: int, *definitions: Audio) -> List[Audio]:
    db = Store()
    pending = []
    for definition in definitions:
        result = db.check(definition)
        if result:
            processed_chat, processed_msg = result['chat_id'], result['message_id']
            bot.forward_message(chat_id, processed_chat, processed_msg)
        else:
            pending.append(definition)
    return pending
