from unittest import mock
from yt_bot.validation.validator import YTLinkValidator


class TestValidator:

    def test_validate(self):
        validator = YTLinkValidator('http://not-exist.xyz')

        assert validator._valid() is False

        validator = YTLinkValidator('https://www.youtube.com/watch?v=$$$$$$$$')

        assert validator._valid() is True

    def test_link_retrieval(self):
        valid_watch_link = 'https://www.youtube.com/watch?v=0000000'
        valid_playlist_link = 'https://www.youtube.com/playlist?list=PLfiMjLyNWxeaFXQ-3GWfMZVF6pnVu_iob'
        invalid_link = 'https://www.youtube.com/'
        validator = YTLinkValidator(valid_watch_link)
        result = validator.valid()
        assert result is True

        validator = YTLinkValidator(valid_playlist_link)
        result = validator.valid()
        assert result is True

        validator = YTLinkValidator(invalid_link)
        result = validator.valid()
        assert result is False

    def test_multiple_link_input(self):
        multiple_input = 'test test https://www.youtube.com/watch?v=xyz test test'
        validator = YTLinkValidator(multiple_input)
        result = validator.valid()
        assert result is False

        multiple_type_input = 'https://www.youtube.com/watch?v=xyz?https://www.youtube.com/playlist?list=PL2E9929257D9B20B7'
        validator = YTLinkValidator(multiple_type_input)
        result = validator.valid()
        assert result is False

    @mock.patch('yt_bot.validation.validator.YTLinkValidator._valid', return_value=True)
    def test_from_not_yt_domain(self, valid_mock):
        link = 'http://not-exist.xyz'
        validator = YTLinkValidator(link)
        res = validator.valid()
        assert res is False


if __name__ == "__main__":
    pass
