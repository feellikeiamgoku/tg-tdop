import os
from unittest.mock import patch, call, Mock

import pytest

from yt_bot.db.redis_store import RedisStore, RateLimiter, LimiterError, RATE_LIMIT


@pytest.fixture
def redis_env():
    os.environ['REDIS_HOST'] = ''
    os.environ['REDIS_PASSWORD'] = ''


class TestRedisStore:

    @patch('yt_bot.db.redis_store.redis.Redis')
    def test_singleton(self, redis, redis_env):
        rs = RedisStore()
        rs2 = RedisStore()
        assert rs is rs2

    @patch('yt_bot.db.redis_store.RedisStore._get_engine')
    def test_get_engine(self, engine):
        rs = RedisStore()
        assert engine.called


class TestRateLimiter:

    @patch('yt_bot.db.redis_store.redis.Redis')
    def test_check_rate(self, engine):
        rl = RateLimiter()
        rl._engine = {12: 10, 111: RATE_LIMIT + 1}

        rate = rl.check_rate(12)
        assert rate == 10

        with pytest.raises(LimiterError):
            rl.check_rate(111)

    @patch('yt_bot.db.redis_store.redis.Redis')
    def test_set_rate(self, engine_call):
        rl = RateLimiter()
        engine_mock = Mock()
        engine_mock.get.return_value = 12
        rl._engine = engine_mock
        rl.set_rate(1)
        engine_mock.incr.assert_called_with(1, 1)

        engine_mock.reset_mock()

        engine_mock.get.return_value = 0
        rl.set_rate(1)
        engine_mock.set.assert_called_with(1, 1, 3600)

        engine_mock.get.return_value = RATE_LIMIT + 1
        with pytest.raises(LimiterError):
            rl.set_rate(1)


pytest.main()
