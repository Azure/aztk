


class AztkError(Exception):
    def __init__(self, message: str = None):
        super().__init__()
        self.message = message

class ClusterNotReadyError(AztkError):
    pass

class AzureApiInitError(AztkError):
    def __init__(self, message: str = None):
        super().__init__()
        self.message = message
