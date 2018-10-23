def try_func(exception_formatter=None, raise_exception=None, catch_exceptions=()):
    import functools

    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except catch_exceptions as e:
                if exception_formatter:
                    raise raise_exception(exception_formatter(e))
                else:
                    raise raise_exception(str(e))

        return wrapper

    return decorator
