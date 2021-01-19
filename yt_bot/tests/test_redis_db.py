import os
from unittest.mock import patch, Mock

import pytest

from yt_bot.constants import RATE_LIMIT
from yt_bot.db.redis_store import RedisStore, RateLimiter, RunningTracker, RunningContext
from yt_bot.errors import RunningContextError, LimiterError


@pytest.fixture(scope='module', autouse=True)
def redis_env():
    os.environ['REDIS_HOST'] = ''
    os.environ['REDIS_PASSWORD'] = ''


class TestRedisStore:

    @patch('yt_bot.db.redis_store.redis.Redis')
    def test_singleton(self, redis):
        rs = RedisStore()
        rs2 = RedisStore()
        assert rs is rs2

    @patch('yt_bot.db.redis_store.RedisStore._get_engine')
    def test_get_engine(self, engine):
        rs = RedisStore()
        assert engine.called


@patch('yt_bot.db.redis_store.redis.Redis')
class TestRateLimiter:

    def test_check_rate(self, engine):
        rl = RateLimiter()
        rl._engine = {12: RATE_LIMIT - 1, 111: RATE_LIMIT + 1}

        rate = rl.check_rate(12)
        assert rate == RATE_LIMIT - 1

        with pytest.raises(LimiterError):
            rl.check_rate(111)

    def test_set_rate(self, engine_call):
        rl = RateLimiter()
        engine_call.get.return_value = 12
        rl._engine = engine_call
        rl.set_rate(1)
        engine_call.incr.assert_called_with(1, 1)

        engine_call.reset_mock()

        engine_call.get.return_value = 0
        rl.set_rate(1)
        engine_call.set.assert_called_with(1, 1, 3600)

        engine_call.get.return_value = RATE_LIMIT + 1
        with pytest.raises(LimiterError):
            rl.set_rate(1)

    @patch('yt_bot.db.redis_store.RateLimiter.check_rate')
    def test_in_limit(self, check_rate, engine_call):
        rl = RateLimiter()
        check_rate.return_value = RATE_LIMIT - 1
        value = rl.in_limit('chat')
        assert value is True

        check_rate.return_value = RATE_LIMIT + 1
        value = rl.in_limit('chat')
        assert value is False


@patch('yt_bot.db.redis_store.redis.Redis')
class TestRunningTracker:

    @pytest.fixture(scope='class')
    def tracker(self):
        return RunningTracker()

    def test_is_running(self, mock_redis, tracker):
        tracker._currently_processing_db = mock_redis
        mock_redis.get.return_value = None

        value = tracker.is_running('id')
        mock_redis.get.assert_called_with('id')
        assert value is False

        mock_redis.reset_mock()

        mock_redis.get.return_value = 'id'
        value = tracker.is_running('id')
        assert value is True

    def test_store_running(self, mock_redis, tracker):
        tracker._currently_processing_db = mock_redis

        tracker.store_running('video_id', 'chat_id')
        mock_redis.set.assert_called_with('video_id', 'chat_id')

    def test_store_waiting(self, mock_redis, tracker):
        tracker._await_processing_db = mock_redis
        tracker.store_waiting('video_id', 'chat_id')

        mock_redis.sadd.assert_called_with('video_id', 'chat_id')

    def test_retrieve_waiting(self, mock_redis, tracker):
        tracker._await_processing_db = mock_redis
        mock_redis.smembers.return_value = {1, 2, 3}

        value = tracker.retrieve_waiting('video_id')

        mock_redis.smembers.assert_called_with('video_id')
        assert value == {1, 2, 3}

    def test_free_internal(self, mock_redis, tracker):
        current_db = Mock()
        await_db = Mock()

        tracker._await_processing_db = await_db
        tracker._currently_processing_db = current_db

        tracker.free('video_id')

        current_db.delete.assert_called_with('video_id')
        await_db.delete.assert_called_with('video_id')

    @patch('yt_bot.db.redis_store.RunningTracker._free_running')
    @patch('yt_bot.db.redis_store.RunningTracker._free_waiting')
    def test_free(self, mock_free_running, mock_free_waiting, mock_redis, tracker):
        tracker.free('video_id')
        mock_free_running.assert_called_with('video_id')
        mock_free_waiting.assert_called_with('video_id')


@patch('yt_bot.db.redis_store.ProcessedStore')
@patch('yt_bot.db.redis_store.redis.Redis')
class TestRunningContext:

    def test_enter_exit(self, mock_redis, mock_db):
        running_context = RunningContext('video_id', 'chat_id')
        running_context._tracker = Mock()
        running_context._rate_limiter = Mock()

        running_context._tracker.is_running.return_value = False

        with running_context as context:
            assert context.running_state is False
            running_context._tracker.is_running.assert_called_with('video_id')

        running_context._tracker.free.assert_called_with('video_id')
        running_context._rate_limiter.set_rate.assert_called_with('chat_id')
        running_context._tracker.reset_mock()

        running_context._tracker.is_running.return_value = True
        with running_context as context:
            assert context.running_state is True
            running_context._tracker.is_running.assert_called_with('video_id')
        running_context._tracker.free.assert_not_called()
        running_context._rate_limiter.assert_not_called()

    @patch('yt_bot.db.redis_store.RunningContext._store_running')
    @patch('yt_bot.db.redis_store.RunningContext._store_waiting')
    def test_enter(self, store_waiting, store_running, mock_redis, mock_db):
        context = RunningContext('video_id', 'chat_id')
        context._tracker = Mock()

        context._tracker.is_running.return_value = False
        with context as c:
            store_running.assert_called()
            store_waiting.assert_not_called()

        context._tracker.is_running.return_value = True
        store_waiting.reset_mock()
        store_running.reset_mock()

        with context as c:
            store_running.assert_not_called()
            store_waiting.assert_called()

    def test_enter_with_rate_limiter(self, mock_redis, mock_db):
        context = RunningContext('video_id', 'chat_id')
        context._rate_limiter = Mock()
        context._tracker = Mock()
        context._rate_limiter.in_limit.return_value = False
        with pytest.raises(LimiterError):
            with context as c:
                pass

    def test_store_running(self, mock_redis, mock_db):
        tracker_mock = Mock()
        running_context = RunningContext('video_id', 'chat_id')
        running_context.running_state = True
        running_context._tracker = tracker_mock

        with pytest.raises(RunningContextError):
            running_context._store_running()

        running_context.running_state = False
        running_context._store_running()
        running_context._tracker.store_running.assert_called_with('video_id','chat_id')

    def test_store_waiting(self, mock_redis, mock_db):
        tracker_mock = Mock()
        running_context = RunningContext('video_id', 'chat_id')
        running_context.running_state = False
        running_context._tracker = tracker_mock

        with pytest.raises(RunningContextError):
            running_context._store_waiting()

        running_context.running_state = True
        running_context._store_waiting()
        running_context._tracker.store_waiting.assert_called_with('video_id', 'chat_id')

pytest.main()