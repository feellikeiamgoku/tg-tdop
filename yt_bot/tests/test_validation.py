import pytest

from yt_bot.validation.definition import ValidationResult, ValidationError, VideoValidator


class TestValidation:

    def test_validation(self):
        web_message = 'https://www.youtube.com/watch?v=RsQXVJOgvNY'
        validator = VideoValidator(web_message)
        result = validator.validate()
        assert isinstance(result, ValidationResult)
        assert result.link == web_message
        assert result.video_id == 'RsQXVJOgvNY'

        mobile_message = 'youtu.be/X2xbLV_NSbk'
        validator = VideoValidator(mobile_message)
        result = validator.validate()
        assert isinstance(result, ValidationResult)
        assert result.link == mobile_message
        assert result.video_id == 'X2xbLV_NSbk'

    def test_validation_errors(self):
        message = 'some invalid message'
        validator = VideoValidator(message)
        with pytest.raises(ValidationError):
            result = validator.validate()

        incomplete_link = 'www.youtu.be/'
        validator = VideoValidator(incomplete_link)
        with pytest.raises(ValidationError):
            result = validator.validate()

        incomplete_link = 'youtube.com/watch?v='
        validator = VideoValidator(incomplete_link)
        with pytest.raises(ValidationError):
            result = validator.validate()

    def test_link_inside_text(self):
        message = 'eg egqweg gew gwe dfiowedg gdj\nhttps://www.youtube.com/watch?v=XXYlFuWEuKf worg gg egqwe'
        validator = VideoValidator(message)
        result = validator.validate()
        assert isinstance(result, ValidationResult)
        assert result.link == 'https://www.youtube.com/watch?v=XXYlFuWEuKf'
        assert result.video_id == 'XXYlFuWEuKf'