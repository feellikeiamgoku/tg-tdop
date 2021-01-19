import re
from typing import NamedTuple


class VideoValidationResult(NamedTuple):
    link: str
    video_id: str


class PlaylistValidationResult(NamedTuple):
    link: str


def validate_video(message: str) -> VideoValidationResult:
    validation_pattern = re.compile(
        r'(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})'
    )

    link = re.search(validation_pattern, message)
    if link:
        full_link = link.group(0)
        video_id = link.group(1)
        return VideoValidationResult(full_link, video_id)


def validate_playlist(message: str) -> PlaylistValidationResult:
    validation_pattern = re.compile(
        r'(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/)(?:playlist\?list=)[^\s](.+)'
    )

    link = re.fullmatch(validation_pattern, message)
    if link:
        return PlaylistValidationResult(link.string)
