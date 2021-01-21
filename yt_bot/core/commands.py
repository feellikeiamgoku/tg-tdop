from yt_bot.core.decorators import catch
from yt_bot.db.redis_store import RateLimiter
from utils import emoji


@catch
def start(update, context) -> None:
	message = f'Hello, friend!\nI\'m a simple YouTube bot-downloader. {emoji.robot}\n' \
			  f'I can help you to convert any YouTube video to mp3. {emoji.rainbow}\n' \
			  f'To get started just send me any link to a video or a playlist. {emoji.smile}'
	context.bot.send_message(chat_id=update.effective_chat.id, text=message)


@catch
def limits(update, context) -> None:
	rate_limiter = RateLimiter()
	rate = rate_limiter.rate_limit - rate_limiter.check_rate(update.effective_chat.id)
	remaining_time = rate_limiter.remaining_time(update.effective_chat.id)
	context.bot.send_message(chat_id=update.effective_chat.id,
							 text=f'You have {rate} downloads for next {remaining_time} minutes')
