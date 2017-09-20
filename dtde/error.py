
class InvalidUserCredentialsError(Exception):
    pass


class ClusterNotReadyError(Exception):
    pass


class ThunderboltError(Exception):
    def __init__(self, message: str = None):
        super().__init__()
        self.message = message


class AzureApiInitError(ThunderboltError):
    def __init__(self, message: str = None):
        super().__init__()
        self.message = message
