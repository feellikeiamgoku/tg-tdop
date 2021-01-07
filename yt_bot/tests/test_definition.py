import pytest
from unittest.mock import patch

from yt_bot.validation.definition import DefineYTLinkType, YTWatch, YTPlaylist
from yt_bot.validation.exceptions import DefinitionError, ValidationError


class TestDefinition:

    def test_define(self):
        definer = DefineYTLinkType('https://www.youtube.com/watch?v=000')

        definition_type = definer.define()
        assert isinstance(definition_type, YTWatch)

        definer = DefineYTLinkType('https://www.youtube.com/playlist?list=PLfiMjLyNWxeaFXQ-3GWfMZVF6pnVu_iob')

        definition_type = definer.define()
        assert isinstance(definition_type, YTPlaylist)

        definer = DefineYTLinkType('http://not-exist.xyz')
        with pytest.raises(ValidationError):
            definer.define()

    @patch('yt_bot.validation.definition.YTLinkValidator.valid', return_value=True)
    def test_with_invalid_validation(self, validation_mock):
        link = 'http://not-exist.xyz'
        definer = DefineYTLinkType(link)
        with pytest.raises(DefinitionError):
            definer.define()