import re
from abc import abstractmethod, ABC

from yt_bot.validation.validator import YTLinkValidator
from yt_bot.validation.exceptions import ValidationError, DefinitionError


class Definition(ABC):
    pass


class YTPlaylist(Definition):
    def __init__(self, link: str):
        self.link = link


class YTWatch(Definition):
    def __init__(self, link: str):
        self.link = link


class DefineLinkType(ABC):

    @abstractmethod
    def define(self):
        pass


class DefineYTLinkType(DefineLinkType):

    def __init__(self, message: str):
        self.message = message
        self.validator = YTLinkValidator(message)

    def define(self) -> Definition:
        if self.validator.valid():
            if 'playlist' in self.message:
                return YTPlaylist(self.message)
            elif 'watch' in self.message:
                return YTWatch(self.message)
            else:
                raise DefinitionError()
        else:
            raise ValidationError()
