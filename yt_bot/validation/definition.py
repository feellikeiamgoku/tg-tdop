import re
import os
from abc import abstractmethod, ABC
from typing import List, Tuple

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
        self.path = None
        self.processed = False

    def set_postprocess_values(self, chat_id, message_id):
        self.chat_id = chat_id
        self.message_id = message_id

    def set_path(self, basedir: str) -> None:
        self.path = os.path.join(basedir, self.filename)

    def mark_processed(self) -> None:
        self.processed = True


class AudioList:
    def __init__(self):
        self.audios: List[Audio] = []

    def add(self, audio: Audio):
        if isinstance(audio, Audio):
            self.audios.append(audio)
        else:
            raise TypeError(f'Got inappropriate type "{type(audio)}"')

    @property
    def unprocessed(self):
        return [audio for audio in self.audios if audio.processed is False]

    @property
    def fully_processed(self):
        return all([audio.processed for audio in self.audios])

    def __iter__(self):
        return iter(self.audios)

    def __len__(self):
        return len(self.unprocessed)


class DefineLinkType(ABC):

    @abstractmethod
    def define(self):
        pass


class DefineYTLinkType(DefineLinkType):

    def __init__(self, message: str):
        self.message = message
        self.ydl = YoutubeDL(YDL_OPTS)

    def define(self) -> AudioList:

        info = self.get_video_info()
        al = AudioList()
        for entry in info:
            filename = self.ydl.prepare_filename(entry)
            audio = Audio(entry.get('id'), filename, entry.get('webpage_url'), entry.get('creator'), entry.get('title'),
                          entry.get('filesize'))
            al.add(audio)
        return al

    def get_video_info(self) -> List[dict]:
        with self.ydl as ydl:
            info = ydl.extract_info(self.message, download=False)
        entries = info.get('entries')
        if isinstance(entries, list) and not entries:
            raise EmptyPlayListError()
        return info.get('entries') or [info]


class ValidationError(Exception):
    pass


class ValidationResult:
    def __init__(self, link: str, video_id: str):
        self.link = link
        self.video_id = video_id


class VideoValidator:
    validation_pattern = re.compile(
        r'(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})'
    )

    def __init__(self, message: str):
        self.message = message

    def validate(self) -> ValidationResult:
        link = re.search(self.validation_pattern, self.message)
        if link:
            full_link = link.group(0)
            video_id = link.group(1)
            return ValidationResult(full_link, video_id)
        else:
            raise ValidationError("Invalid youtube link.")
