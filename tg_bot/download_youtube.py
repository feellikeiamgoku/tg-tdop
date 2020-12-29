import os

from contextlib import contextmanager

import youtube_dl


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': False
}

@contextmanager
def download_mp3(url, config=ydl_opts):
    with youtube_dl.YoutubeDL(config) as ydl:
        info = ydl.extract_info(url)
        yt_id, title = info['id'], info['title']
    title = rename_file(yt_id, title)
    yield title
    os.remove(title)


def find_file(yt_id: str):
    #handle file not found
    files = os.listdir()
    for file in files:
        if yt_id in file:
            return file


def rename_file(yt_id: str, to: str):
    filename = find_file(yt_id)
    os.rename(filename, to)
    return to
