class EmptyPlayListError(Exception):
    def __init__(self):
        self.msg = 'Empty playlist, please, check out your playlist.'
        super().__init__(self.msg)