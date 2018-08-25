import time

import pytest

from aztk.utils import BackOffPolicy, retry


def test_retry_function_raises_allowed_exception():
    with pytest.raises(ValueError):

        @retry(exceptions=(ValueError))
        def raise_allowed_error():
            raise ValueError

        raise_allowed_error()


def test_retry_function_raises_diallowed_exception():
    with pytest.raises(FileExistsError):

        @retry(exceptions=(ValueError))
        def raise_disallowed_error():
            raise FileExistsError

        raise_disallowed_error()


def test_retry_function_retry_count():
    # use a mutable type to test number retries
    my_list = []
    with pytest.raises(ValueError):

        @retry(retry_count=3, exceptions=(ValueError))
        def my_func():
            my_list.append(0)
            raise ValueError

        my_func()

    assert len(my_list) == 3


def test_retry_function_retry_interval():
    with pytest.raises(ValueError):

        @retry(retry_count=2, retry_interval=1, exceptions=(ValueError))
        def my_func():
            raise ValueError

        start = time.time()
        my_func()
        end = time.time()
        assert int(end - start) == 2


def test_retry_function_backoff_policy_linear():
    with pytest.raises(ValueError):

        @retry(retry_count=2, retry_interval=1, exceptions=(ValueError))
        def my_func():
            raise ValueError

        start = time.time()
        my_func()
        end = time.time()
        assert int(end - start) == 2    # 1 + 1


def test_retry_function_backoff_policy_exponential():
    @retry(retry_count=4, retry_interval=1, backoff_policy=BackOffPolicy.exponential, exceptions=(ValueError))
    def my_func():
        raise ValueError

    start = time.time()
    try:
        my_func()
    except ValueError:
        pass
    end = time.time()
    print(end - start)
    assert int(end - start) == 7    # 2**0 + 2**1 + 2**3
