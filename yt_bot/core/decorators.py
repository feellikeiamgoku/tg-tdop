import logging
import traceback

from typing import Union
from functools import wraps
from telegram import Update, ParseMode

from yt_bot.core.handlers import ForwardUpdate, AudioUpdate
from yt_bot.errors import UnknownType
from yt_bot.core.response import resp
from utils.env import get_env


def catch(func):

	@wraps(func)
	def wrap(update: Union[Update, AudioUpdate, ForwardUpdate], context):
		try:
			func(update, context)
		except Exception as e:
			logging.error(e)

			dev_chat_id = get_env('DEV_CHAT')

			if isinstance(update, (AudioUpdate, ForwardUpdate)):
				chat_id = update.chat_id
				message = update.validation_result.link
			elif isinstance(update, Update):
				chat_id = update.effective_chat.id
				message = update.message.text
			else:
				raise UnknownType(f'Got unknown type: "{type(update)}"')

			context.bot.send_message(chat_id, text=resp.UNHANDLED_ERROR)

			trace = ''.join(traceback.format_tb(e.__traceback__))

			to_dev_message = f'Hey\nUnhandled error happened in chat: <i>{chat_id}</i>,' \
							 f' while processing message: <b>{message}</b>.\n' \
							 f'View full traceback:\n<code>{trace}</code>'

			context.bot.send_message(dev_chat_id, text=to_dev_message, parse_mode=ParseMode.HTML)

	return wrap
