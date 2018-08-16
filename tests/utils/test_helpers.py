from aztk.utils import helpers


def test_bool_env():
    assert helpers.bool_env(True) == "true"
    assert helpers.bool_env(False) == "false"
    assert helpers.bool_env(None) == "false"
    assert helpers.bool_env("some") == "false"
