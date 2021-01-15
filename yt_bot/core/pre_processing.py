from telegram.bot import Bot

from utils import emoji
from yt_bot.core.exceptions import UserInputError
from yt_bot.core.mixins import TelegramMixin
from yt_bot.db.store import ProcessedStore
from yt_bot.validation.validators import VideoValidator, ValidationResult, ValidationError


class PreDownload(TelegramMixin):

    def __init__(self, chat_id: str, message: str, bot: Bot):
        self._chat_id = chat_id
        self._bot = bot
        self._validator = VideoValidator(message)
        self._db = ProcessedStore()

    def check(self) -> ValidationResult:
        """Do checks before start processing"""
        try:
            validation_result = self._validator.validate()
            self.notify(f'Processing your video... {emoji.robot}')
        except ValidationError:
            raise UserInputError()

        to_forward = self.get_to_forward(validation_result)
        validation_result.set_forward(to_forward)
        return validation_result

    def get_to_forward(self, validation_result: ValidationResult):
        result = self._db.check(validation_result.video_id)
        return result or None
