import warnings
import functools
import inspect


def deprecated(version: str, advice: str = None):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    Args:
        version (str): The version in which the deprecated functionality will be removed
        advice (str): Sentence explaining alternatives to the deprecated functionality.
    """

    def decorator(func):
        if inspect.isclass(func):
            msg = "Call to deprecated class {name}."
        else:
            msg = "Call to deprecated function {name}."

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            deprecate(version=version, message=msg.format(name=func.__name__, advice=advice), advice=advice)
            return func(*args, **kwargs)

        return new_func

    return decorator


def deprecate(version: str, message: str, advice: str = ""):
    """
    Print a deprecation warning.

    Args:
        message (str): Sentence explaining what is deprecated.
        advice (str): Sentence explaining alternatives to the deprecated functionality.
    """

    warnings.simplefilter("always", DeprecationWarning)    # turn off filter
    warnings.warn(
        "{0} It will be removed in Aztk version {1}. {2}".format(message, version, advice),
        category=DeprecationWarning,
        stacklevel=2,
    )
    warnings.simplefilter("default", DeprecationWarning)    # reset filter
