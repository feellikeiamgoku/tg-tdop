import os
import logging
from abc import ABC

from youtube_dl import YoutubeDL, DownloadError
from telegram.bot import Bot

from yt_bot.db.processedstore import ProcessedStore
from yt_bot.constants import YDL_OPTS
from yt_bot.validation.validators import VideoValidator, ValidationResult
from yt_bot.validation.exceptions import ValidationError
from yt_bot.yt.context import DirContext

from utils import emoji


class UserInputError(Exception):
    def __init__(self, msg=None):
        self.msg = msg or f'Invalid link {emoji.exclamation_mark}'
        super().__init__(self.msg)


class AbstractProcessor(ABC):

    def notify(self, msg) -> None:
        self._bot.send_message(chat_id=self._chat_id, text=msg)


class PreDownload(AbstractProcessor):

    def __init__(self, chat_id: str, message: str, bot: Bot):
        self._chat_id = chat_id
        self._bot = bot
        self._validator = VideoValidator(message)
        self._db = ProcessedStore()

    def check(self) -> ValidationResult:

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


class DownloadProcessor(AbstractProcessor):
    def __init__(self, chat_id: str, message_id: str, message: str, bot: Bot):
        self._chat_id = chat_id
        self._message_id = message_id
        self._message = message
        self._bot = bot
        self._pre_processor = PreDownload(chat_id, message, bot)
        self._post_processor = PostDownload()

        self._allowed_size = 49_000_000

    def run(self):
        validation_result = self._pre_processor.check()
        if validation_result.forward:
            for reply in validation_result.forward:
                self.forward(reply.chat_id, reply.message_id)
            return

        with DirContext(self._chat_id, self._message_id) as context:
            filename = self.download()
            path = os.path.join(os.getcwd(), filename)
            if self.large_file(path):
                raise UserInputError("Video is too large, can't handle it for now")
            try:
                msg = self._bot.send_audio(self._chat_id, open(path, 'rb'), timeout=1000)
            except Exception as e:
                logging.error(e)
            else:
                self._post_processor.post_save(self._chat_id, msg.message_id, validation_result.video_id,
                                               validation_result.link)

    def download(self) -> str:
        try:
            with YoutubeDL(YDL_OPTS) as ydl:
                info = ydl.extract_info(self._message)
                filename = ydl.prepare_filename(info)
            return filename
        except DownloadError:
            raise UserInputError()

    def forward(self, from_chat_id, message_id) -> None:
        self._bot.forward_message(self._chat_id, from_chat_id, message_id)

    def large_file(self, filepath) -> bool:
        filesize = os.stat(filepath).st_size
        if filesize > self._allowed_size:
            return True
        return False


class PostDownload:
    def __init__(self):
        self._db = ProcessedStore()

    def post_save(self, chat_id, message_id, video_id, link):
        self._db.save(chat_id, message_id, video_id, link, part=1)


if __name__ == '__main__':
    pass
