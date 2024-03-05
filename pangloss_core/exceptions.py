class PanglossConfigError(Exception):
    pass


class PanglossCreateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class PanglossNotFoundError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
