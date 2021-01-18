import re
from abc import ABC, abstractmethod
from typing import Iterable


class ValidationResult:
    def __init__(self, link: str, video_id: str):
        self.link = link
        self.video_id = video_id
        self.forward = None

    def set_forward(self, to_forward: Iterable) -> None:
        if isinstance(to_forward, Iterable) and to_forward:
            self.forward = to_forward


class PlaylistValidationResult:
    def __init__(self, link: str):
        self.link = link


class BaseValidator(ABC):

    def __init__(self, message: str):
        self.message = message

    @abstractmethod
    def validate(self):
        pass


class VideoValidator(BaseValidator):
    validation_pattern = re.compile(
        r'(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})'
    )

    def validate(self) -> ValidationResult:
        link = re.search(self.validation_pattern, self.message)
        if link:
            full_link = link.group(0)
            video_id = link.group(1)
            return ValidationResult(full_link, video_id)


class PlaylistValidator(BaseValidator):
    validation_pattern = re.compile(
        r'(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/)(?:playlist\?list=)[^\s](.+)'
    )

    def validate(self) -> PlaylistValidationResult:
        link = re.fullmatch(self.validation_pattern, self.message)
        if link:
            return PlaylistValidationResult(link.string)
