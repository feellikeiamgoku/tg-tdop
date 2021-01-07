import os
import pathlib
from youtube_dl import YoutubeDL

from yt_bot.yt.context import DirContext
from yt_bot.validation.definition import YTWatch

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
    def __init__(self, filename: str, author: str, link: str):
        self.filename = filename
        self.author = author
        self.link = link
        self.path = self.get_path()

    def get_path(self):
        return pathlib.Path(os.path.join(os.getcwd(), self.filename))


def download(url) -> Audio:
    with YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(url, download=True)
        file_name = ydl.prepare_filename(video_info)
        return Audio(file_name, video_info['creator'], url)


if __name__ == "__main__":
    with DirContext(1235, 23):
        audio = download(
            'https://www.youtube.com/watch?v=rc5_UTxvnZQ&list=PLfiMjLyNWxeaFXQ-3GWfMZVF6pnVu_iob&index=2')
