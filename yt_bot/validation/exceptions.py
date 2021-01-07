
class DefinitionError(Exception):
    def __init__(self):
        self.message = "Youtube link doesn't match playlist type or video type."
        super().__init__(self.message)


class ValidationError(Exception):
    def __init__(self):
        self.message = "Invalid link, please send link from youtube.com"
        super().__init__(self.message)
