import os
import re
from typing import NamedTuple, BinaryIO
import urllib.request
from youtube_dl import YoutubeDL, DownloadError

from yt_bot.constants import YDL_OPTS


class Downloaded(NamedTuple):
    title: str = None
    author: str = None
    file: BinaryIO = None
    duration: int = None
    thumbnail: BinaryIO = None
    exception: str = None

    def __str__(self):
        return self.title


class Downloader:
    def __init__(self, link: str):
        self._link = link
        self._allowed_size = 49_000_000
        self._ydl  = YoutubeDL(YDL_OPTS)

    def get_downloaded(self) -> Downloaded:

        downloaded = self.download()
        if not downloaded.exception and self.large_file(downloaded.file):
            downloaded.exception = 'File is too large, can\'t handle it for now!'
        return downloaded

    def download(self) -> Downloaded:
        try:
            info = self._ydl.extract_info(self._link)
            title = self.prepare_title(info['title'])
            author = info['creator'] or info['uploader']
            file = self._get_file(info)
            thumbnail = urllib.request.urlopen(info['thumbnail'])
            downloaded = Downloaded(title, author, file, info['duration'], thumbnail)
            return downloaded

        except DownloadError as e:
            message = self._prepare_error_message(e.args[0])
            return Downloaded(exception=message)

    def large_file(self, file) -> bool:
        filesize = os.fstat(file.fileno()).st_size
        if filesize > self._allowed_size:
            return True
        return False

    def _prepare_error_message(self, message: str) -> str:
        if 'video is not available' in message or 'Video unavailable' in message:
            return f'Video unavailable {self._link}'
        message = message.replace('ERROR:', '')
        return message.split('.')[0]

    @staticmethod
    def prepare_title(title: str) -> str:
        pattern = re.compile(r'((([-\s]*\(.+\)[-\s]*)|([-\s]*\[.+\][-\s]*)))')
        return re.sub(pattern, '', title)

    def _get_file(self, info: dict) -> BinaryIO:
        filename = self._ydl.prepare_filename(info)
        file_path = os.path.join(os.getcwd(), filename)
        file = open(file_path, 'rb')
        os.remove(file_path)
        return file


if __name__ == '__main__':
    pass
