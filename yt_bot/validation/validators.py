import re
from typing import Iterable

from yt_bot.validation.exceptions import ValidationError


class ValidationResult:
    def __init__(self, link: str, video_id: str):
        self.link = link
        self.video_id = video_id
        self.forward = None

    def set_forward(self, to_forward: Iterable) -> None:
        if isinstance(to_forward, Iterable) and to_forward:
            self.forward = to_forward


class VideoValidator:
    validation_pattern = re.compile(
        r'(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})'
    )

    def __init__(self, message: str):
        self.message = message

    def validate(self) -> ValidationResult:
        link = re.search(self.validation_pattern, self.message)
        if link:
            full_link = link.group(0)
            video_id = link.group(1)
            return ValidationResult(full_link, video_id)
        else:
            raise ValidationError("Invalid youtube link.")
