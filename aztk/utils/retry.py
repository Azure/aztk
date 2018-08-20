import functools
import time
from enum import Enum


class BackOffPolicy(Enum):
    linear = "linear"
    exponential = "exponential"


def retry(retry_count=1, retry_interval=0, backoff_policy=BackOffPolicy.linear, exceptions=()):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            for i in range(retry_count - 1):
                try:
                    return function(*args, **kwargs)
                except exceptions:
                    if backoff_policy == BackOffPolicy.linear:
                        time.sleep(i * retry_interval)
                    if backoff_policy == BackOffPolicy.exponential:
                        print("sleeping:", 2**(i * retry_interval))
                        time.sleep(2**(i * retry_interval))
            # do not retry on the last iteration
            return function(*args, **kwargs)

        return wrapper

    return decorator
