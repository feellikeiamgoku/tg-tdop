import logging
import os

from telegram.bot import Bot
from youtube_dl import YoutubeDL, DownloadError

from yt_bot.constants import YDL_OPTS
from yt_bot.core.exceptions import UserInputError
from yt_bot.core.mixins import TelegramMixin
from yt_bot.core.post_processing import PostDownload
from yt_bot.core.pre_processing import PreDownload
from yt_bot.db.redis_store import RunningVidTracker


class Download(TelegramMixin):
    def __init__(self, chat_id: str, message_id: str, message: str, bot: Bot):
        self._chat_id = chat_id
        self._message_id = message_id
        self._message = message
        self._bot = bot
        self._pre_processor = PreDownload(chat_id, message, bot)
        self._post_processor = PostDownload()
        self._tracker = RunningVidTracker()
        self._allowed_size = 49_000_000

    def run(self):
        validation_result = self._pre_processor.check()
        if validation_result.forward:
            for reply in validation_result.forward:
                self.forward(reply.chat_id, reply.message_id)
            return

        if not self._tracker.is_running(validation_result.video_id):
            self._tracker.store_running(validation_result.video_id, self._chat_id)
        else:
            self._tracker.store_waiting(validation_result.video_id, self._chat_id)
            return

        try:
            filename = self.download()
            path = os.path.join(os.getcwd(), filename)
            if self.large_file(path):
                raise UserInputError("Video is too large, can't handle it for now")
            try:
                msg = self.send_audio(path)
            except Exception as e:
                logging.error(e)
            else:
                os.remove(path)
                self._post_processor.post_save(self._chat_id, msg.message_id, validation_result.video_id,
                                               validation_result.link)
                self._post_processor.update_rate(self._chat_id)
                waiting = self._tracker.retrieve_waiting(validation_result.video_id)
                for chat in waiting:
                    self.forward(self._chat_id, msg.message_id, to_chat=chat)
        finally:
            self._tracker.free(validation_result.video_id)

    def download(self) -> str:
        try:
            with YoutubeDL(YDL_OPTS) as ydl:
                info = ydl.extract_info(self._message)
                filename = ydl.prepare_filename(info)
            return filename
        except DownloadError:
            raise UserInputError()

    def large_file(self, filepath) -> bool:
        filesize = os.stat(filepath).st_size
        if filesize > self._allowed_size:
            return True
        return False


if __name__ == '__main__':
    pass
