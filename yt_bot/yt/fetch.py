import os
from youtube_dl import YoutubeDL
from yt_bot.constants import YDL_OPTS


def download(url) -> str:
    base_path = os.getcwd()
    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url)
        filename = ydl.prepare_filename(info)
    return os.path.join(base_path, filename)


if __name__ == "__main__":
    download('https://www.youtube.com/watch?v=dCETckUx97o')
