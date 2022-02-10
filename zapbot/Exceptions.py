class VariableNotDefined(Exception):
    """Exception raised if no chat is open.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, variable: str, message="Variable {} not defined"):
        self.message = message.format(variable)
        super().__init__(self.message)

    def __str__(self):
        return self.message

