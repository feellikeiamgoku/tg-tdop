from yt_bot.db.redis_store import RateLimiter, RATE_LIMIT
from yt_bot.db.store import ProcessedStore
from yt_bot.validation.validators import VideoValidator, ValidationResult
from yt_bot.validation.exceptions import ValidationError


class LimitError(Exception):
    pass


class Checker:

    def __init__(self, chat_id: str, message: str):
        self._chat_id = chat_id
        self._validator = VideoValidator(message)
        self._db = ProcessedStore()
        self._rate_limiter = RateLimiter()

    def check(self) -> ValidationResult:
        """Do checks before start processing"""
        validation_result = self._validator.validate()
        if validation_result:
            forwarded = self.check_forwarded(validation_result.video_id)
            if forwarded:
                validation_result.set_forward(forwarded)
                return validation_result
            elif self.in_limits():
                return validation_result
            else:
                raise LimitError('Out of limits.')
        else:
            raise ValidationError('Invalid link')

    def check_forwarded(self, video_id: str):
        result = self._db.check(video_id)
        return result or None

    def in_limits(self):
        rate = self._rate_limiter.check_rate(self._chat_id)
        if rate >= RATE_LIMIT:
            return False
        return True
