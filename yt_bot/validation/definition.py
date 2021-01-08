import os
from abc import abstractmethod, ABC
from typing import List

from youtube_dl import YoutubeDL
from yt_bot.constants import YDL_OPTS
from yt_bot.validation.exceptions import EmptyPlayListError


class Audio:
    def __init__(self, video_id: str, filename: str, link: str, author: str = None, title: str = None,
                 filesize: int = None):
        self.video_id = video_id
        self.filename = filename
        self.link = link
        self.author = author
        self.title = title
        self.filesize = filesize
        self.message_id = None
        self.chat_id = None

    def set_postprocess_values(self, chat_id, message_id):
        self.chat_id = chat_id
        self.message_id = message_id

    def get_path(self):
        return os.path.join(os.getcwd(), self.filename)


class DefineLinkType(ABC):

    @abstractmethod
    def define(self):
        pass


class DefineYTLinkType(DefineLinkType):

    def __init__(self, message: str):
        self.message = message
        self.ydl = YoutubeDL(YDL_OPTS)

    def define(self) -> List[Audio]:

        info = self.get_video_info()
        entries = []
        for entry in info:
            filename = self.ydl.prepare_filename(entry)
            audio = Audio(entry.get('id'), filename, entry.get('webpage_url'), entry.get('creator'), entry.get('title'),
                          entry.get('filesize'))
            entries.append(audio)
        return entries

    def get_video_info(self) -> List[dict]:
        with self.ydl as ydl:
            info = ydl.extract_info(self.message, download=False)
        entries = info.get('entries')
        if isinstance(entries, list) and not entries:
            raise EmptyPlayListError()
        return info.get('entries') or [info]
