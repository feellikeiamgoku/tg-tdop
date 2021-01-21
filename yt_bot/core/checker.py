from typing import Union, NamedTuple

from pytube import Playlist

from yt_bot.core.validators import validate_playlist, validate_video, VideoValidationResult, \
    PlaylistValidationResult
from yt_bot.errors import UnknownType
from yt_bot.core.response import resp as resp
from yt_bot.constants import RATE_LIMIT


class CheckerErrorMessage(NamedTuple):
    msg: str


class Checker:
    def __init__(self, message: str):
        self.message = message

    def check(self) -> Union[VideoValidationResult, CheckerErrorMessage]:
        """Do checks before start processing"""
        validation_result = self.validate(self.message)

        if isinstance(validation_result, PlaylistValidationResult):
            playlist = Playlist(validation_result.link)
            if len(playlist) > 0:
                for video_url in playlist.video_urls[:RATE_LIMIT]:
                    playlist_item = self.validate(video_url)
                    if isinstance(playlist_item, VideoValidationResult):
                        yield playlist_item
                    else:
                        raise UnknownType(f'Got unknown validation type "{type(validation_result)}"')
            else:
                yield CheckerErrorMessage(resp.EMPTY_PLAYLIST)
        elif isinstance(validation_result, VideoValidationResult) or isinstance(validation_result, CheckerErrorMessage):
            yield validation_result
        else:
            raise UnknownType(f'Got unknown validation type "{type(validation_result)}"')

    @staticmethod
    def validate(message: str) -> Union[VideoValidationResult, PlaylistValidationResult, CheckerErrorMessage]:
        validation_result = validate_video(message) or validate_playlist(message)
        return validation_result if validation_result else CheckerErrorMessage(resp.INVALID_LINK)

    def __iter__(self):
        return self.check()

