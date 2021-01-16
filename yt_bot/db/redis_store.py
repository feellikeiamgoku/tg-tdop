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
                           **kwargs)


class RateLimiter(RedisStore):
    def __init__(self):
        super().__init__(decode_responses=True)
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


if __name__ == '__main__':
    pass
