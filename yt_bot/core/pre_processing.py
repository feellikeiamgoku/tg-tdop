from typing import Tuple, Union

from youtube_dl import DownloadError

from utils import emoji
from yt_bot.validation.definition import DefineYTLinkType, AudioList, EmptyPlayListError
from yt_bot.db.store import Store


def get_definition(message: str) -> Tuple[Union[AudioList, None], str]:
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


def check_processed(al: AudioList):
    db = Store()
    for audio in al:
        result = db.check(audio)
        if result:
            audio.mark_processed()
            yield result['chat_id'], result['message_id']
