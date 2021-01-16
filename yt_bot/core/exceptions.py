from utils import emoji


class UserInputError(Exception):
    def __init__(self, msg=None):
        self.msg = msg or f'Invalid link {emoji.exclamation_mark}'
        super().__init__(self.msg)


class UserLimitError(Exception):
    def __init__(self, ttl, msg=None):
        minutes = int(ttl) // 60
        self.msg = msg or f'You are off limits {emoji.red_light}\nWait {minutes} minutes before next video processing.'
        super().__init__(self.msg)
