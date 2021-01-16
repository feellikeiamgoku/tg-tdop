from yt_bot.db.redis_store import RateLimiter
from yt_bot.db.store import ProcessedStore


class PostDownload:
    def __init__(self):
        self._db = ProcessedStore()

        self._rate_limiter = RateLimiter()

    def post_save(self, chat_id, message_id, video_id, link, part=1):
        self._db.save(chat_id, message_id, video_id, link, part=part)

    def update_rate(self, chat_id):
        self._rate_limiter.set_rate(chat_id)
