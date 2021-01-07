import os
from abc import abstractmethod, ABC
from typing import List

from youtube_dl import YoutubeDL

from yt_bot.validation.exceptions import ValidationError, DefinitionError

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.mp3',
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True
}


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
        self.ydl = YoutubeDL(ydl_opts)

    def define(self) -> List[Audio]:
        with self.ydl as ydl:
            info = ydl.extract_info(self.message, download=False)
            if isinstance(info, dict):
                filename = ydl.prepare_filename(info)
                audio = Audio(info['id'], filename, info['webpage_url'], info['creator'], info['title'],
                              info['filesize'])
                return [audio]
            elif isinstance(info, list):
                entries = []
                for entry in info['entries']:
                    filename = ydl.prepare_filename(entry)
                    audio = Audio(entry['id'], filename, info['webpage_url'], entry['creator'], entry['title'],
                                  entry['filesize'])
                    entries.append(audio)
                return entries
