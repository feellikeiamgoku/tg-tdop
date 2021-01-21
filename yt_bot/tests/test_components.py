import os
from unittest.mock import Mock, patch, PropertyMock
from inspect import isgenerator
from io import BytesIO
from urllib.error import URLError, HTTPError

import pytest

from yt_bot.core.checker import Checker, CheckerErrorMessage
from yt_bot.core.validators import VideoValidationResult, PlaylistValidationResult
from yt_bot.errors import UnknownType
from yt_bot.core.response import resp
from yt_bot.core.downloader import Downloader, DownloaderErrorMessage, Downloaded, DownloadError


class TestChecker:

	@pytest.fixture(scope='class')
	def checker(self):
		return Checker('message')

	@patch('yt_bot.core.checker.Checker.check')
	def test_iter_calls(self, check_mock, checker):
		iter(checker)
		checker.check.assert_called()

	def test_iter_return_value(self, checker):
		res = iter(checker)
		assert isgenerator(res)

	@patch('yt_bot.core.checker.validate_video', return_value=False)
	@patch('yt_bot.core.checker.validate_playlist', return_value='playlist')
	def test_validate_validate_video_false(self, validate_playlist, validate_video, checker):
		res = checker.validate('message')
		validate_playlist.assert_called_with('message')
		assert res == 'playlist'

	@patch('yt_bot.core.checker.validate_video', return_value='video')
	@patch('yt_bot.core.checker.validate_playlist')
	def test_validate_validate_video_true(self, validate_playlist, validate_video, checker):
		res = checker.validate('message')
		validate_video.assert_called_with('message')
		validate_playlist.assert_not_called()
		assert res == 'video'

	@patch('yt_bot.core.checker.validate_video', return_value=False)
	@patch('yt_bot.core.checker.validate_playlist', return_value=False)
	def test_validate_validate_both_false(self, validate_playlist, validate_video, checker):
		result = checker.validate('message')
		assert isinstance(result, CheckerErrorMessage)

	@patch('yt_bot.core.checker.Checker.validate', return_value=VideoValidationResult('link', 'id'))
	def test_check_with_video_validation_result(self, validate_mock, checker):
		value = next(checker.check())
		assert isinstance(value, VideoValidationResult)
		assert value.link == 'link'
		assert value.video_id == 'id'

	def test_check_with_error_validation_result(self, checker):
		value = next(checker.check())
		assert isinstance(value, CheckerErrorMessage)
		assert value.msg == resp.INVALID_LINK

	@patch('yt_bot.core.checker.Checker.validate', return_value='some string')
	def test_check_with_default_input(self, validate_mock, checker):
		with pytest.raises(UnknownType):
			next(checker.check())

	@patch('yt_bot.core.checker.Checker.validate', return_value=PlaylistValidationResult('link'))
	def test_check_with_playlist_validation_result(self, validate_mock):
		checker = Checker('message')
		with patch('yt_bot.core.checker.Playlist'):
			with patch('yt_bot.core.checker.len', return_value=0):
				value = next(checker.check())
				assert isinstance(value, CheckerErrorMessage)
				assert value.msg == resp.EMPTY_PLAYLIST

		checker = Checker('message')
		with patch('yt_bot.core.checker.Playlist') as playlist_call:
			with patch('yt_bot.core.checker.len', return_value=1):
				type(playlist_call.return_value).video_urls = PropertyMock(return_value=[1, 2, 3])
				with pytest.raises(UnknownType):
					value = next(checker.check())

				validate_mock.return_value = VideoValidationResult('link', 'id')
				value = next(checker.check())
				assert isinstance(value, VideoValidationResult)


class TestDownloader:

	@pytest.fixture(scope='class')
	def downloader(self):
		return Downloader('link')

	def test_prepare_title(self, downloader):
		title = downloader._prepare_title('(some value) - title --(some value)')
		assert title == 'title'

		title = downloader._prepare_title('[some value] - title - [some value]')
		assert title == 'title'

		title = downloader._prepare_title('title - [some value]')
		assert title == 'title'

	@patch('yt_bot.core.downloader.YoutubeDL.prepare_filename', return_value='mock_file.mp3')
	def test_get_file(self, prepare_filename, downloader):
		with open('mock_file.mp3', 'w') as f:
			f.write('some info')

		file = downloader._get_file({})
		assert file.read() == b'some info'

	@patch('yt_bot.core.downloader.os.fstat')
	def test_large_file(self, fstat, downloader):
		io = open('tmp.txt', 'w')
		type(fstat.return_value).st_size = PropertyMock(return_value=10)
		value = downloader.large_file(io)
		assert value is False

		type(fstat.return_value).st_size = PropertyMock(return_value=downloader._allowed_size + 1)
		value = downloader.large_file(io)
		assert value is True

		os.remove('tmp.txt')

	@patch('yt_bot.core.downloader.urllib.request.urlopen', return_value='thumb')
	def test_get_thumbnail(self, urlopen, downloader):
		thumb = downloader._get_thumbnail('link')
		assert 'thumb' == thumb

		urlopen.side_effect = ValueError('error')
		thumb = downloader._get_thumbnail('link')
		assert isinstance(thumb, BytesIO)

		urlopen.side_effect = URLError('error')
		thumb = downloader._get_thumbnail('link')
		assert isinstance(thumb, BytesIO)

		urlopen.side_effect = HTTPError('url', 1, 'error', {}, open('tmp.txt', 'w'))
		thumb = downloader._get_thumbnail('link')
		assert isinstance(thumb, BytesIO)

		urlopen.side_effect = TypeError('error')
		with pytest.raises(TypeError):
			thumb = downloader._get_thumbnail('link')

		os.remove('tmp.txt')

	@patch('yt_bot.core.downloader.YoutubeDL.extract_info')
	def test_download(self, ydl, downloader):
		ydl.side_effect = DownloadError('Error')
		value = downloader.download()
		isinstance(value, DownloaderErrorMessage)

		ydl.reset_mock()
		ydl.return_value = {}
		value = downloader.download()
		isinstance(value, dict)

	@patch('yt_bot.core.downloader.Downloader.download')
	def test_downloaded(self, download_mock, downloader):
		download_mock.return_value = DownloaderErrorMessage('msg')
		value = downloader.get_downloaded()
		assert isinstance(value, DownloaderErrorMessage)

		download_mock.return_value = 'msg'
		with pytest.raises(UnknownType):
			value = downloader.get_downloaded()

		downloader.large_file = Mock()
		downloader.download.return_value = {}
		with patch('yt_bot.core.downloader.Downloader._get_file'):
			downloader.large_file.return_value = True
			value = downloader.get_downloaded()
			assert isinstance(value, DownloaderErrorMessage)

			downloader.large_file.return_value = False
			with patch('yt_bot.core.downloader.Downloader._get_thumbnail', return_value=BytesIO()):
				value = downloader.get_downloaded()
				assert isinstance(value, Downloaded)
				assert value.title == 'DefaultTitle'
				assert isinstance(value.thumbnail, BytesIO)
				assert value.author is None
				assert value.duration == 0


pytest.main()
