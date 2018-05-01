import warnings
import functools
import inspect
import aztk.version as version

def deprecated(reason: str = None):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    Args:
        reason (str): Reason to why this class or function is being deprecated
    """

    def decorator(func):
        if inspect.isclass(func):
            msg = "Call to deprecated class {name} ({reason})."
        else:
            msg = "Call to deprecated function {name} ({reason})."

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            deprecate(msg.format(func.__name__, reason))
            return func(*args, **kwargs)
        return new_func

    return decorator


def deprecate(message: str):
    """
    Print a deprecate warning.

    Args:
        message (str): Message to print
    """

    deprecated_version = _get_deprecated_version()
    warnings.simplefilter('always', DeprecationWarning)  # turn off filter
    warnings.warn("{0} It will be removed in Aztk version {1}".format(message, deprecated_version),
                  category=DeprecationWarning,
                  stacklevel=2)
    warnings.simplefilter('default', DeprecationWarning)  # reset filter


def _get_deprecated_version():
    """
    Returns the next version where the deprecated funtionality will be removed
    """
    if version.major == 0:
        return "0.{minor}.0".format(minor=version.minor + 1)
    return "{major}.0.0".format(major=version.major + 1)
