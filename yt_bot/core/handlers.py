import logging
from typing import NamedTuple

from telegram.bot import Bot
from telegram.error import TimedOut, NetworkError
from telegram.ext.handler import Handler

from yt_bot.core.checker import Checker, LimitError
from yt_bot.core.downloader import Downloader
from yt_bot.db.redis_store import RunningContext
from yt_bot.validation.exceptions import ValidationError
from yt_bot.validation.validators import ValidationResult


class AudioUpdate(NamedTuple):
	chat_id: int
	message_id: int
	validation_result: ValidationResult


class ValidationHandler(Handler):

	def check_update(self, update) -> AudioUpdate:
		if isinstance(update, AudioUpdate):
			if not update.validation_result.forward:
				return update
			else:
				raise Exception('Send for further processing with ready to forward results')


def pre_download_check(update, context) -> None:
	message = update.message.text
	chat_id = update.effective_chat.id
	message_id = update.effective_message.message_id
	bot: Bot = context.bot
	checker = Checker(chat_id, message)
	try:
		validation_result = checker.check()
	except LimitError:
		bot.send_message(chat_id=chat_id, text='You\'re off limits!')
	except ValidationError:
		bot.send_message(chat_id=chat_id, text='Invalid link!')
	else:
		if validation_result.forward:
			for reply in validation_result.forward:
				bot.forward_message(chat_id, reply.chat_id, reply.message_id)
		else:
			audio_update = AudioUpdate(chat_id, message_id, validation_result)
			context.update_queue.put(audio_update)
		bot.delete_message(chat_id, message_id)


def process_file(update: AudioUpdate, context) -> None:
	bot: Bot = context.bot

	with RunningContext(update.validation_result.video_id, update.chat_id) as tracker:
		if not tracker.running_state:
			downloader = Downloader(update.validation_result.link)
			downloaded = downloader.get_downloaded()
			if downloaded.exception:
				msg = bot.send_message(chat_id=update.chat_id, text=downloaded.exception)
			else:
				try:
					msg = bot.send_audio(update.chat_id, downloaded.file,
										 downloaded.duration, downloaded.author,
										 downloaded.title, timeout=1000, thumb=downloaded.thumbnail)
				except (TimedOut, NetworkError) as tg_error:
					msg = bot.send_message(update.chat_id,
										   text='Something bad happen while sending your audio, please try again later')
					logging.error(tg_error)
				else:
					tracker.update(msg.message_id, update.validation_result.link)

			waiting = tracker.retrieve_waiting()
			for chat in waiting:
				if int(chat) != update.chat_id:
					bot.forward_message(chat, update.chat_id, msg.message_id)
