from utils import emoji


class UserInputError(Exception):
    def __init__(self, msg=None):
        self.msg = msg or f'Invalid link {emoji.exclamation_mark}'
        super().__init__(self.msg)
