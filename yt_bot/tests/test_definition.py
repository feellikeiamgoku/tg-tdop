import pytest
from unittest.mock import patch

from yt_bot.validation.definition import DefineYTLinkType, EmptyPlayListError
from yt_bot.core.pre_processing import get_definition


class TestDefinition:

    @patch('yt_bot.validation.definition.YoutubeDL.extract_info')
    def test_get_video_info(self, mock):
        definer = DefineYTLinkType('link')
        mock.return_value = {'entries': []}
        with pytest.raises(EmptyPlayListError):
            info = definer.get_video_info()
            assert mock.called is True

        mock.reset_mock()
        mocked_value = {'some_value': 1, 'some_another_value': 2}
        mock.return_value = mocked_value
        info = definer.get_video_info()
        assert [mocked_value] == info

        mock.reset_mock()
        mocked_value = {'some_value': 1, 'some_another_value': 2, 'entries': [1, 2, 3]}
        mock.return_value = mocked_value
        info = definer.get_video_info()
        assert [1, 2, 3] == info

    @patch('yt_bot.validation.definition.YoutubeDL.extract_info')
    def test_define(self, mock):
        mock.return_value = {'id': 'id'}
        definer = DefineYTLinkType('link')
        result = definer.define()
        assert len(result) == 1

        mock.reset_mock()
        mock.return_value = {'entries': [{'id': 1}, {'id': 2}]}
        result = definer.define()
        assert len(result) == 2

    @patch('yt_bot.core.pre_processing.Bot')
    @patch('yt_bot.core.pre_processing.DefineYTLinkType.define')
    def test_get_definition(self, mock_define, mock_bot):
        get_definition('message', mock_bot, 123)


pytest.main()
