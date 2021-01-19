from utils import emoji


class Response:
    INVALID_LINK = f'Invalid link! {emoji.exclamation_mark}\nPlease, check your link and try again {emoji.smile}'
    EMPTY_PLAYLIST = f'Empty playlist! {emoji.exclamation_mark}\nPlease, check your link and try again {emoji.smile}'


response = Response()