class ChatListNotFoundException(Exception):
    """Exception raised if we cant found a chat.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Chat list not found"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.target} -> {self.message}'

class ChatNotFoundException(Exception):
    """Exception raised if we cant found a chat.

    Attributes:
        target -- chat requested
        message -- explanation of the error
    """

    def __init__(self, target, message="Chat not found"):
        self.target = target
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.target} -> {self.message}'

class NoOpenChatException(Exception):
    """Exception raised if no chat is open.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="No open chat found, try calling ZapAPI.open_chat(<chat_name>) first."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message