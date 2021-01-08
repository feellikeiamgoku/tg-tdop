from typing import List, Tuple, Union

from youtube_dl import DownloadError
from telegram.bot import Bot

from utils import emoji
from yt_bot.validation.definition import DefineYTLinkType, Audio, EmptyPlayListError
from yt_bot.db.store import Store


def get_definition(message: str) -> Tuple[Union[List[Audio], None], str]:
    """Returns definition and message for further sending"""

    try:
        definer = DefineYTLinkType(message)
        to_process = definer.define()
    except DownloadError:
        return None, f'Invalid link, please, take a look at provided link {emoji.exclamation_mark}'
    except EmptyPlayListError as e:
        return None, f'{e.msg} {emoji.exclamation_question_mark_selector}'
    else:
        return to_process, f'Processing your video... {emoji.robot}'


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
