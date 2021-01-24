from yt_bot.core.validators import (
    VideoValidationResult,
    validate_video,
    validate_playlist,
    PlaylistValidationResult)


class TestVideoValidation:

    def test_validation(self):
        web_message = 'https://www.youtube.com/watch?v=RsQXVJOgvNY'
        result = validate_video(web_message)
        assert isinstance(result, VideoValidationResult)
        assert result.link == web_message
        assert result.video_id == 'RsQXVJOgvNY'

        mobile_message = 'youtu.be/X2xbLV_NSbk'
        result = validate_video(mobile_message)
        assert isinstance(result, VideoValidationResult)
        assert result.link == mobile_message
        assert result.video_id == 'X2xbLV_NSbk'

    def test_invalid_validation(self):
        message = 'some invalid message'
        result = validate_video(message)
        assert result is None

        incomplete_link = 'www.youtu.be/'
        result = validate_video(incomplete_link)
        assert result is None

        incomplete_link = 'youtube.com/watch?v='
        result = validate_video(incomplete_link)
        assert result is None

    def test_link_inside_text(self):
        message = 'eg egqweg gew gwe dfiowedg gdj\nhttps://www.youtube.com/watch?v=XXYlFuWEuKf worg gg egqwe'
        result = validate_video(message)
        assert isinstance(result, VideoValidationResult)
        assert result.link == 'https://www.youtube.com/watch?v=XXYlFuWEuKf'
        assert result.video_id == 'XXYlFuWEuKf'


class TestPlaylistValidator:
    def test_validation(self):
        message = 'https://www.youtube.com/playlist?list=PLHZ8Vq26Cys9-CrgqrFIYqR1Flp3OLqYr'
        result = validate_playlist(message)
        assert isinstance(result, PlaylistValidationResult)
        assert result.link == message

        message = 'youtube.com/playlist?list=PLHZ8Vq26Cys9-CrgqrFIYqR1Flp3OLqYr'
        result = validate_playlist(message)
        assert isinstance(result, PlaylistValidationResult)
        assert result.link == message

    def test_invalid_validation(self):
        message = 'https://www.youtube.com/playlist?list= dgsd'
        result = validate_playlist(message)
        assert result is None

        message = 'https://www.youtube.com/watch?v=RsQXVJOgvNY'
        result = validate_playlist(message)
        assert result is None
