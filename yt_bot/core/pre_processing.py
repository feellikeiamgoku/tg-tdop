from typing import List

from yt_bot.validation.definition import DefineYTLinkType, YTWatch, YTPlaylist, Definition
from yt_bot.validation.exceptions import DefinitionError, ValidationError
from yt_bot.db.store import Store


def get_definition(message: str, bot: 'Bot', chat_id: int) -> Definition:
    try:
        definer = DefineYTLinkType(message)
        to_process = definer.define()
    except (ValidationError, DefinitionError) as e:
        bot.send_message(chat_id=chat_id, text=e.message)
    else:
        bot.send_message(chat_id=chat_id, text="Processing your video...")
        return to_process


def check_processed(bot: 'Bot', chat_id: int, *definitions: YTWatch) -> List[YTWatch]:
    db = Store()
    pending = []
    for definition in definitions:
        result = db.check(definition)
        if result:
            processed_chat, processed_msg = result
            bot.forward_message(chat_id, processed_chat, processed_msg)
        else:
            pending.append(definition)
    return pending
