import pytest

import aztk.utils.deprecation
from aztk.models import Model, fields
from aztk.utils.deprecation import deprecate, deprecated


def test_deprecated_function():
    @deprecated(version="0.0.0")
    def deprecated_function():
        pass

    with pytest.warns(DeprecationWarning):
        deprecated_function()


def test_deprecated_class():
    @deprecated(version="0.0.0")
    class DeprecatedClass:
        pass

    with pytest.warns(DeprecationWarning):
        DeprecatedClass()


def test_deprecated_field():
    class DummyClass(Model):
        non_deprecated_field = fields.Boolean()

        def __init__(self, *args, **kwargs):
            if 'deprecated_field' in kwargs:
                deprecate("0.0.0", "deprecated_field is deprecated for DummyClass.",
                          "Please use non_deprecated_field instead.")
                kwargs['non_deprecated_field'] = kwargs.pop('deprecated_field')

            super().__init__(*args, **kwargs)

        @property
        @deprecated("0.0.0")
        def deprecated_field(self):
            return self.non_deprecated_field

        @deprecated_field.setter
        @deprecated("0.0.0")
        def deprecated_field(self, value):
            self.non_deprecated_field = value

    with pytest.warns(DeprecationWarning) as deprecation_warning:
        dummy_class = DummyClass(deprecated_field=True)
        assert dummy_class.deprecated_field is True

    assert dummy_class.non_deprecated_field is True
    assert "deprecated_field is deprecated for DummyClass." in str(deprecation_warning[0].message)
    assert "Please use non_deprecated_field instead." in str(deprecation_warning[0].message)


def test_deprecate_version():
    with pytest.warns(DeprecationWarning) as deprecation_warning:
        deprecate("0.0.0", "message")

    assert "0.0.0" in str(deprecation_warning[0].message)

    with pytest.warns(DeprecationWarning) as deprecation_warning:
        deprecate("0.1.0", "message")

    assert "0.1.0" in str(deprecation_warning[0].message)


def test_deprecate_message():
    with pytest.warns(DeprecationWarning) as deprecation_warning:
        deprecate("0.0.0", message="test message")

    assert "0.0.0" in str(deprecation_warning[0].message)
    assert "test message" in str(deprecation_warning[0].message)


def test_deprecate_advice():
    with pytest.warns(DeprecationWarning) as deprecation_warning:
        deprecate("0.0.0", message="test message", advice="use this instead")

    assert "use this instead" in str(deprecation_warning[0].message)
