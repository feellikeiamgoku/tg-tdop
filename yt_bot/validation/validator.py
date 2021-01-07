import re
from abc import abstractmethod, ABC
from yt_bot.validation.exceptions import ValidationError, DefinitionError


class LinkValidator(ABC):

    @abstractmethod
    def valid(self) -> bool:
        pass


class YTLinkValidator(LinkValidator):
    base_url = 'https://www.youtube.com/'
    retrieval_pattern = re.compile(
        r"(^https://www\.youtube\.com/watch\?v=[a-zA-Z0-9]+$)|(^https://www\.youtube\.com/playlist\?list=.+$)"
    )

    def __init__(self, message: str):
        self.message = message

    def _valid(self) -> bool:
        """Simple validator. Assert that link comes from youtube.com"""
        return self.base_url in self.message

    def valid(self) -> bool:
        """Retrieve full link from given message"""
        if self._valid():
            link = re.search(self.retrieval_pattern, self.message)
            return True if link else False
        else:
            return False
