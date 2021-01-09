from typing import Tuple, Union

from youtube_dl import DownloadError

from utils import emoji
from yt_bot.validation.definition import DefineYTLinkType, AudioList, EmptyPlayListError
from yt_bot.db.store import Store

from yt_bot.validation.definition import VideoValidator, ValidationError, ValidationResult


def get_definition(message: str) -> Tuple[Union[None,ValidationResult], str]:
    """Returns definition and message for further sending"""
    try:
        validator = VideoValidator(message)
        to_process = validator.validate()
    except ValidationError:
        return None, f'Invalid link, please, take a look at provided link {emoji.exclamation_mark}'
    else:
        return to_process, f'Processing your video... {emoji.robot}'


def check_processed(al: AudioList):
    db = Store()
    for audio in al:
        result = db.check(audio)
        if result:
            audio.mark_processed()
            yield result['chat_id'], result['message_id']
