"""
Contains all errors used in Aztk.
All error should inherit from `AztkError`
"""


class AztkError(Exception):
    pass


class AztkAttributeError(AztkError):
    pass


class ClusterNotReadyError(AztkError):
    pass


class AzureApiInitError(AztkError):
    pass


class InvalidPluginConfigurationError(AztkError):
    pass


class InvalidModelError(AztkError):
    def __init__(self, message: str, model=None):
        super().__init__()
        self.message = message
        self.model = model

    def __str__(self):
        model_name = self.model and self.model.__class__.__name__
        return "{model} {message}".format(model=model_name, message=self.message)


class MissingRequiredAttributeError(InvalidModelError):
    pass


class InvalidCustomScriptError(InvalidModelError):
    pass


class InvalidPluginReferenceError(InvalidModelError):
    pass


class InvalidModelFieldError(InvalidModelError):
    def __init__(self, message: str, model=None, field=None):
        super().__init__(message, model)
        self.field = field

    def __str__(self):
        model_name = self.model and self.model.__class__.__name__
        return "{model} {field} {message}".format(model=model_name, field=self.field, message=self.message)
