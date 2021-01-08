from typing import List

from yt_bot.validation.definition import DefineYTLinkType, Audio, EmptyPlayListError
from yt_bot.db.store import Store

from youtube_dl import DownloadError


def get_definition(message: str, bot: 'Bot', chat_id: int) -> List[Audio]:
    try:
        definer = DefineYTLinkType(message)
        to_process = definer.define()
    except DownloadError:
        bot.send_message(chat_id=chat_id, text='Invalid link, please, take a look at provided link.')
    except EmptyPlayListError as e:
        bot.send_message(chat_id=chat_id, text=e.msg)
    else:
        bot.send_message(chat_id=chat_id, text="Processing your video...")
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
