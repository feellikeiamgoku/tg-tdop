from utils import emoji


class Response:
    INVALID_LINK = f'Invalid link{emoji.exclamation_mark}\nPlease, check your link and try again.{emoji.smile}'
    EMPTY_PLAYLIST = f'Empty playlist{emoji.exclamation_mark}\nPlease, check your link and try again.{emoji.smile}'
    OUT_OF_LIMIT = f'You are off limits{emoji.exclamation_mark}\nPlease, check your limits and try again.'
    SENDING_ERROR = lambda self, link: f'Something bad happen while sending your audio{emoji.sad}from link: {link}\nPlease try again later.'
    LARGE_FILE = lambda self, link: f'Video {link} is too large{emoji.exclamation_mark}\nCan\'t send it for now.{emoji.sad}'
    UNAVAILABLE_VIDEO = lambda self, link: f'Video {link} is unavailable{emoji.exclamation_mark}'
    UNHANDLED_ERROR = f'Sorry, something bad happen on my side{emoji.sad}\nAll guilty will be punished!{emoji.angry}'


resp = Response()