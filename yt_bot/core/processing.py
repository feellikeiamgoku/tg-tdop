import os

from yt_bot.yt.fetch import download
from yt_bot.yt.context import DirContext
from yt_bot.validation.definition import AudioList


def process(chat_id: int, message_id: int, al: AudioList):
    with DirContext(chat_id, message_id):
        base = os.getcwd()
        for audio in al.unprocessed:
            download(audio.link)
            audio.set_path(base)
            yield audio
