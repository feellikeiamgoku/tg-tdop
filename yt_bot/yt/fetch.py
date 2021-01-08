from youtube_dl import YoutubeDL
from yt_bot.constants import YDL_OPTS


def download(url):
    with YoutubeDL(YDL_OPTS) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    download('https://www.youtube.com/watch?v=dCETckUx97o')
