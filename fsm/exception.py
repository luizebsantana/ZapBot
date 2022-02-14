class InvalidStateException(Exception):
    def __init__(self, state, message="Invalid state '{}'"):
        self.state = state
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message.format(self.state)

class InvalidKeywordException(Exception):
    def __init__(self, keyword, message="Invalid keyword '{}'"):
        self.keyword = keyword
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return self.message.format(self.keyword)