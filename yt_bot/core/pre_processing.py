from typing import Tuple, Union

from utils import emoji
from yt_bot.db.processedstore import ProcessedStore

from yt_bot.validation.validators import VideoValidator, ValidationError, ValidationResult


def get_further_processing(message: str) -> Tuple[Union[ValidationResult, None], str]:
    """Returns definition and message for further sending"""
    try:
        validator = VideoValidator(message)
        validation_result = validator.validate()
    except ValidationError:
        return None, f'Invalid link, please, take a look at provided link {emoji.exclamation_mark}'
    else:
        return validation_result, f'Processing your video... {emoji.robot}'


def check_processed(video_id: str):
    db = ProcessedStore()
    result = db.check(video_id)
    if result:
        return str(result['chat_id']), str(result['message_id'])
