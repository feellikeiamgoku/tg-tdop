from unittest.mock import Mock, patch, PropertyMock
from inspect import isgenerator
import pytest

from yt_bot.core.checker import Checker, CheckerErrorMessage
from yt_bot.core.validators import VideoValidationResult, PlaylistValidationResult
from yt_bot.errors import UnknownType
from yt_bot.core.response import resp


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

	def test_check_with_default_input(self, checker):
		with pytest.raises(UnknownType):
			next(checker.check())

	@patch('yt_bot.core.checker.Checker.validate', return_value=PlaylistValidationResult('link'))
	def test_check_with_playlist_validation_result(self, validate_mock):
		checker = Checker('message')
		with patch('yt_bot.core.checker.Playlist', return_value=[]):
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

pytest.main()