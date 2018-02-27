"""
Contains all errors used in Aztk.
All error should inherit from `AztkError`
"""



class AztkError(Exception):
    def __init__(self, message: str = None):
        super().__init__(message)

class ClusterNotReadyError(AztkError):
    pass

class AzureApiInitError(AztkError):
    pass

class InvalidPluginConfigurationError(AztkError):
    pass

class InvalidModelError(AztkError):
    pass

class MissingRequiredAttributeError(InvalidModelError):
    pass

class InvalidCustomScriptError(InvalidModelError):
    pass

class InvalidPluginReferenceError(InvalidModelError):
    pass
