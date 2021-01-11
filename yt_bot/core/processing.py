import os

from yt_bot.yt.fetch import download
from yt_bot.yt.context import DirContext


def process(link: str):
    path = download(link)
    return path
