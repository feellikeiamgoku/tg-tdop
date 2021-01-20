from typing import Union, NamedTuple

from pytube import Playlist

from yt_bot.core.validators import validate_playlist, validate_video, VideoValidationResult, \
    PlaylistValidationResult
from yt_bot.core.response import response as resp


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
                for video_url in playlist.video_urls[:25]:
                    yield self.validate(video_url)
            else:
                yield CheckerErrorMessage(resp.EMPTY_PLAYLIST)
        else:
            yield validation_result

    @staticmethod
    def validate(message: str) -> Union[VideoValidationResult, PlaylistValidationResult, CheckerErrorMessage]:
        validation_result = validate_video(message) or validate_playlist(message)
        return validation_result if validation_result else CheckerErrorMessage(resp.INVALID_LINK)

    def __iter__(self):
        return self.check()

