import logging

from telegram import Bot, ChatAction
from telegram.error import TimedOut, NetworkError

from yt_bot.core.checker import Checker, CheckerErrorMessage
from yt_bot.core.downloader import Downloader, DownloaderErrorMessage
from yt_bot.core.handlers import ForwardUpdate, AudioUpdate
from yt_bot.db.redis_store import RunningContext
from yt_bot.db.store import ProcessedStore
from yt_bot.errors import LimiterError
from yt_bot.core.response import resp
from yt_bot.core.decorators import catch


@catch
def pre_download_check(update, context) -> None:
	message = update.message.text
	chat_id = update.effective_chat.id
	message_id = update.effective_message.message_id
	bot: Bot = context.bot
	store = ProcessedStore()
	checker = Checker(message)
	deleted = False
	for validation_result in checker:
		if isinstance(validation_result, CheckerErrorMessage):
			bot.send_message(chat_id=chat_id, text=validation_result.msg)
		else:
			forwarded = store.check(validation_result.video_id)
			if forwarded:
				audio_update = ForwardUpdate(forwarded.chat_id, forwarded.message_id, chat_id, same_chat=True)
			else:
				audio_update = AudioUpdate(chat_id, validation_result)

			context.update_queue.put(audio_update)
			if not deleted:
				bot.delete_message(chat_id, message_id)
				deleted = True


@catch
def process_file(update: AudioUpdate, context) -> None:
	bot: Bot = context.bot
	try:
		with RunningContext(update.validation_result.video_id, update.chat_id) as tracker:
			bot.send_chat_action(chat_id=update.chat_id, action=ChatAction.UPLOAD_AUDIO)
			if not tracker.running_state:
				downloader = Downloader(update.validation_result.link)
				downloaded = downloader.get_downloaded()
				if isinstance(downloaded, DownloaderErrorMessage):
					msg = bot.send_message(chat_id=update.chat_id, text=downloaded.msg)
				else:
					try:
						msg = bot.send_audio(update.chat_id, downloaded.file,
											 downloaded.duration, downloaded.author,
											 downloaded.title, timeout=1000, thumb=downloaded.thumbnail)
					except (TimedOut, NetworkError) as tg_error:
						msg = bot.send_message(update.chat_id,
											   text=resp.SENDING_ERROR(update.validation_result.link))
						logging.error(tg_error)
					else:
						tracker.update(msg.message_id, update.validation_result.link)

				waiting = tracker.retrieve_waiting()
				forward_upd = ForwardUpdate(update.chat_id, msg.message_id, *waiting)
				context.update_queue.put(forward_upd)
	except LimiterError:
		bot.send_message(chat_id=update.chat_id, text=resp.OUT_OF_LIMIT)


@catch
def forward(update: ForwardUpdate, context):
	bot: Bot = context.bot

	for chat in update.chats:
		if int(chat) != update.from_chat or update.same_chat:
			bot.forward_message(chat, update.from_chat, update.message_id)
