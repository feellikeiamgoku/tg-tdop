import redis

from utils.env import get_env
from yt_bot.constants import RATE_LIMIT
from yt_bot.db.store import Store


class LimiterError(Exception):
    pass


class RedisStore(Store):

    def __init__(self, **kwargs):
        self._engine = self._get_engine(**kwargs)

    @staticmethod
    def _get_engine(**kwargs):
        return redis.Redis(host=get_env('REDIS_HOST'),
                           password=get_env('REDIS_PASSWORD'),
                           decode_responses=True,
                           **kwargs)


class RateLimiter(RedisStore):
    def __init__(self):
        super().__init__()
        self._rate_limit = RATE_LIMIT

    def check_rate(self, chat_id):
        used_calls = int(self._engine.get(chat_id) or 0)
        if used_calls > self._rate_limit:
            raise LimiterError('Get calls value more then limit value')
        return used_calls

    def set_rate(self, chat_id):
        rate = self.check_rate(chat_id)
        if rate >= self._rate_limit:
            raise LimiterError('Trying to increment off limit value')
        elif rate >= 1:
            self._engine.incr(chat_id, 1)
        else:
            self._engine.set(chat_id, 1, 3600)

    def remaining_time(self, chat_id):
        time = self._engine.ttl(chat_id) or 0
        return time


class RunningVidTracker(RedisStore):

    def __init__(self):
        self._currently_processing_db = self._get_engine(db=0)
        self._await_processing_db = self._get_engine(db=1)

    def store_running(self, video_id: str, chat_id: str):
        if not self.is_running(video_id):
            self._currently_processing_db.set(video_id, chat_id)
        else:
            raise Exception('Store while running.')

    def is_running(self, video_id: str) -> bool:
        return bool(self._currently_processing_db.get(video_id))

    def store_waiting(self, video_id: str, chat_id: str):
        if self.is_running(video_id):
            self._await_processing_db.sadd(video_id, chat_id)
        else:
            raise Exception('Store waiting, while no running')

    def retrieve_waiting(self, video_id: str):
        chats = self._await_processing_db.smembers(video_id)
        return chats

    def free(self, video_id: str):
        self._free_running(video_id)
        self._free_waiting(video_id)

    def _free_running(self, video_id: str):
        self._currently_processing_db.delete(video_id)

    def _free_waiting(self, video_id: str):
        self._await_processing_db.delete(video_id)


if __name__ == '__main__':
    pass
