import pytest

from aztk.error import AztkError, AztkAttributeError
from aztk.models.plugins.internal import PluginReference, PluginTarget, PluginTargetRole


def test_from_dict():
    ref = PluginReference.from_dict(
        dict(
            name="my-test-script",
            script="path/to/script.sh",
            target="host",
            target_role="worker",
        ))

    assert ref.name == "my-test-script"
    assert ref.script == "path/to/script.sh"
    assert ref.target == PluginTarget.Host
    assert ref.target_role == PluginTargetRole.Worker


def test_from_dict_invalid_param():
    with pytest.raises(AztkAttributeError):
        PluginReference.from_dict(dict(name2="invalid"))


def test_from_dict_invalid_target():
    with pytest.raises(AztkError):
        PluginReference.from_dict(dict(
            script="path/to/script.sh",
            target="host-invalid",
        ))


def test_from_dict_invalid_target_role():
    with pytest.raises(AztkError):
        PluginReference.from_dict(dict(
            script="path/to/script.sh",
            target_role="worker-invalid",
        ))
