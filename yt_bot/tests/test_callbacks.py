import os

from unittest.mock import patch, Mock, MagicMock
from io import BytesIO

import pytest
from telegram.error import TimedOut

from yt_bot.core.callbacks import process_file, pre_download_check, forward, CheckerErrorMessage, \
	VideoValidationResult, LimiterError, resp, DownloaderErrorMessage, Downloaded, catch
from yt_bot.core.commands import limits, RateLimiter
from yt_bot.core.handlers import ForwardUpdate, AudioUpdate
from yt_bot.db.store import ForwardResult
from yt_bot.errors import UnknownType


@pytest.fixture
def update_context():
	update = Mock()
	context = Mock()

	update.message.text = 'callback_message'
	update.effective_chat.id = 'callback_chat_id'
	update.effective_message.message_id = 'callback_message_id'
	update.chat_id = 'callback_chat_id'
	update.validation_result.link = 'callback_link'
	return update, context


@pytest.fixture(scope='module', autouse=True)
def set_dev_chat():
	os.environ['DEV_CHAT'] = 'xyz'


class TestCallbacks:

	@patch('yt_bot.core.callbacks.Checker.__iter__')
	@patch('yt_bot.core.callbacks.ProcessedStore')
	def test_pre_download_with_forward(self, store_cls, checker, update_context):
		upd, context = update_context
		checker.return_value = iter([CheckerErrorMessage('test_message'), VideoValidationResult('link', 'video_id'),
									 VideoValidationResult('link', 'video_id')])
		store = Mock()
		store_cls.return_value = store
		with patch('yt_bot.core.callbacks.ForwardUpdate') as fupd:
			with patch('yt_bot.core.callbacks.AudioUpdate') as aupd:
				store.check.return_value = ForwardResult('forward_chat_id', 'forward_message')
				pre_download_check(upd, context)
				context.bot.send_message.assert_called_with(chat_id='callback_chat_id', text='test_message')
				fupd.assert_called_with('forward_chat_id', 'forward_message', 'callback_chat_id', same_chat=True)
				aupd.assert_not_called()
			context.update_queue.put.assert_called()
			context.bot.delete_message.assert_called_once()

	@patch('yt_bot.core.callbacks.Checker.__iter__')
	@patch('yt_bot.core.callbacks.ProcessedStore')
	def test_pre_download_with_no_forward(self, store_cls, checker, update_context):
		upd, context = update_context
		checker.return_value = iter([CheckerErrorMessage('test_message'), VideoValidationResult('link', 'video_id'),
									 VideoValidationResult('link', 'video_id'), None])
		store = Mock()
		store_cls.return_value = store
		with patch('yt_bot.core.callbacks.ForwardUpdate') as fupd:
			with patch('yt_bot.core.callbacks.AudioUpdate') as aupd:
				store.check.return_value = None
				with pytest.raises(UnknownType):
					pre_download_check(upd, context)
				context.bot.send_message.assert_called_with(chat_id='callback_chat_id', text='test_message')
				fupd.assert_not_called()
				aupd.assert_called_with('callback_chat_id', VideoValidationResult('link', 'video_id'))
			context.update_queue.put.assert_called()
			context.bot.delete_message.assert_called_once()

	def test_forward(self, update_context):
		upd, context = update_context
		upd = ForwardUpdate('123', '123', '321', same_chat=True)
		forward(upd, context)
		context.bot.forward_message.assert_called_with('321', '123', '123')

		context.bot.forward_message.reset_mock()

		upd = ForwardUpdate('123', '123', '123', same_chat=False)
		forward(upd, context)
		context.bot.forward_message.assert_not_called()

		upd = ForwardUpdate('123', '123', '123', same_chat=True)
		forward(upd, context)
		context.bot.forward_message.assert_called_with('123', '123', '123')

	@patch('yt_bot.core.callbacks.RunningContext')
	def test_process_file_with_limit_error(self, running_context, update_context):
		upd, context = update_context
		running_context.side_effect = LimiterError('limit error')
		process_file(upd, context)
		context.bot.send_message.assert_called_with(chat_id='callback_chat_id', text=resp.OUT_OF_LIMIT)

	@patch('yt_bot.core.callbacks.RunningContext')
	@patch('yt_bot.core.callbacks.Downloader')
	def test_process_file_with_running_state(self, downloader, running_context, update_context):
		upd, context = update_context
		tracker = MagicMock()
		running_context.return_value.__enter__.return_value = tracker
		tracker.running_state = True
		process_file(upd, context)
		downloader.assert_not_called()

	@patch('yt_bot.core.callbacks.RunningContext')
	@patch('yt_bot.core.callbacks.Downloader')
	def test_process_file_with_no_running_state_with_error(self, downloader_cls, running_context, update_context):
		upd, context = update_context
		tracker = MagicMock()
		downloader = Mock()
		downloader_cls.return_value = downloader
		running_context.return_value.__enter__.return_value = tracker
		tracker.running_state = False
		downloader.get_downloaded.return_value = DownloaderErrorMessage('error')

		process_file(upd, context)

		downloader_cls.assert_called_with('callback_link')
		context.bot.send_message.assert_called_with(chat_id='callback_chat_id', text='error')

	@patch('yt_bot.core.callbacks.RunningContext')
	@patch('yt_bot.core.callbacks.Downloader')
	def test_process_file_with_no_running_state(self, downloader_cls, running_context, update_context):
		upd, context = update_context
		tracker = MagicMock()
		downloader = Mock()
		downloader_cls.return_value = downloader
		running_context.return_value.__enter__.return_value = tracker
		tracker.running_state = False
		thumb = BytesIO()
		file = BytesIO()
		downloader.get_downloaded.return_value = Downloaded('title', 'author', file, 0, thumb)

		process_file(upd, context)
		context.bot.send_audio.assert_called_with('callback_chat_id', file, 0, 'author', 'title', timeout=1000,
												  thumb=thumb)
		tracker.update.assert_called()
		tracker.reset_mock()

		context.bot.send_audio.side_effect = TimedOut()
		process_file(upd, context)
		context.bot.send_message.assert_called_with('callback_chat_id', text=resp.SENDING_ERROR('callback_link'))
		tracker.update.assert_not_called()
		tracker.retrieve_waiting.assert_called()
		context.update_queue.put.assert_called()


def test_fallback_decorator(update_context):
	update = AudioUpdate(123, VideoValidationResult('link', 'video_id'))
	upd, context = update_context

	def some_func():
		raise

	wrap = catch(some_func)
	wrap(update, context)
	context.bot.send_message.assert_called()


@patch('yt_bot.core.commands.RateLimiter')
def test_limit_command(limiter_cls, update_context):
	upd, context = update_context
	limiter = Mock()
	limiter_cls.return_value = limiter
	limiter.rate_limit = 20
	limiter.check_rate.return_value = 10
	limiter.remaining_time.return_value = 888

	limits(upd, context)

	context.bot.send_message.assert_called_with(chat_id='callback_chat_id',
												text=f'You have 10 downloads for next 888 minutes')


pytest.main()
