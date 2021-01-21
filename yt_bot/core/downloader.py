import os
import re
import urllib.request
from urllib.error import URLError, HTTPError
from typing import NamedTuple, Union, IO
from io import BytesIO
from youtube_dl import YoutubeDL, DownloadError

from yt_bot.constants import YDL_OPTS
from yt_bot.core.response import resp
from yt_bot.errors import UnknownType


class Downloaded(NamedTuple):
	title: str = None
	author: str = None
	file: BytesIO = None
	duration: int = None
	thumbnail: BytesIO = None

	def __str__(self):
		return self.title


class DownloaderErrorMessage(NamedTuple):
	msg: str


class Downloader:
	def __init__(self, link: str):
		self._link = link
		self._allowed_size = 49_000_000
		self._ydl = YoutubeDL(YDL_OPTS)

	def get_downloaded(self) -> Union[Downloaded, DownloaderErrorMessage]:

		video_info = self.download()
		if isinstance(video_info, dict):
			file = self._get_file(video_info)
			if self.large_file(file):
				return DownloaderErrorMessage(resp.LARGE_FILE(self._link))
			else:
				title = self._prepare_title(video_info.get('title', 'DefaultTitle'))
				thumbnail = self._get_thumbnail(video_info.get('thumbnail', ''))
				author = video_info.get('creator') or video_info.get('uploader')
				duration = video_info.get('duration', 0)
				downloaded = Downloaded(title, author, file, duration, thumbnail)
		elif isinstance(video_info, DownloaderErrorMessage):
			return video_info
		else:
			raise UnknownType(f'Got unknown type {type(video_info)}')
		return downloaded

	def download(self) -> Union[dict, DownloaderErrorMessage]:
		try:
			return self._ydl.extract_info(self._link)
		except DownloadError as e:
			message = self._prepare_error_message(e.args[0])
			return DownloaderErrorMessage(message)

	def large_file(self, file: IO) -> bool:
		file_size = os.fstat(file.fileno()).st_size
		if file_size > self._allowed_size:
			return True
		return False

	def _prepare_error_message(self, message: str) -> str:
		# todo cover more cases from ydl exceptions

		if 'video is not available' in message or 'Video unavailable' in message:
			return resp.UNAVAILABLE_VIDEO(self._link)
		message = message.replace('ERROR:', '')
		return message.split('.')[0]

	@staticmethod
	def _prepare_title(title: str) -> str:
		pattern = re.compile(
			r'(((\b[-\s]*\(.+\)[-\s]*)|([-\s]*\(.+\)[-\s]*\b)|(\b[-\s]*\[.+\][-\s]*))|([-\s]*\[.+\][-\s]*)\b)')
		return re.sub(pattern, '', title)

	def _get_file(self, info: dict) -> IO:
		filename = self._ydl.prepare_filename(info)
		file_path = os.path.join(os.getcwd(), filename)
		file = open(file_path, 'rb')
		os.remove(file_path)
		return file

	@staticmethod
	def _get_thumbnail(thumb_link: str) -> BytesIO:
		try:
			return urllib.request.urlopen(thumb_link)
		except (ValueError, URLError, HTTPError):
			return BytesIO()


if __name__ == '__main__':
	pass
