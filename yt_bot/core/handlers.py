from typing import NamedTuple, Union

from telegram.ext.handler import Handler

from yt_bot.core.checker import VideoValidationResult


class AudioUpdate(NamedTuple):
	chat_id: int
	validation_result: VideoValidationResult


class ForwardUpdate:
	def __init__(self, from_chat: str, message_id: str, *chats, same_chat=False):
		self.from_chat = from_chat
		self.message_id = message_id
		self.chats = chats
		self.same_chat = same_chat


class AudioHandler(Handler):

	def __init__(self, listen_cls, *args, **kwargs):
		self.listen_cls = listen_cls
		super().__init__(*args, **kwargs)

	def check_update(self, update) -> Union[AudioUpdate, ForwardUpdate]:
		if isinstance(update, self.listen_cls):
			return update

