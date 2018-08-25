import yaml

from aztk.error import InvalidModelError, InvalidModelFieldError, AztkError, AztkAttributeError
from aztk.core.models import fields


# pylint: disable=W0212,no-member
class ModelMeta(type):
    """
    Model Meta class. This takes all the class definition and build the attributes form all the fields definitions.
    """

    def __new__(mcs, name, bases, attrs):
        attrs["_fields"] = {}

        for base in bases:
            if hasattr(base, "_fields"):
                for k, v in base._fields.items():
                    attrs["_fields"][k] = v
            for k, v in base.__dict__.items():
                if isinstance(v, fields.Field):
                    attrs["_fields"][k] = v

        for k, v in attrs.items():
            if isinstance(v, fields.Field):
                attrs["_fields"][k] = v

        return super().__new__(mcs, name, bases, attrs)


class Model(metaclass=ModelMeta):
    """
    Base class for all aztk models

    To implement model wide validation implement `__validate__` method
    """

    def __new__(cls, *_args, **_kwargs):
        model = super().__new__(cls)
        model._data = {}
        model._defaults = {}
        return model

    def __init__(self, **kwargs):
        self._update(kwargs)

    def __getitem__(self, k):
        if k not in self._fields:
            raise AztkAttributeError("{0} doesn't have an attribute called {1}".format(self.__class__.__name__, k))

        return getattr(self, k)

    def __setitem__(self, k, v):
        if k not in self._fields:
            raise AztkAttributeError("{0} doesn't have an attribute called {1}".format(self.__class__.__name__, k))
        try:
            setattr(self, k, v)
        except InvalidModelFieldError as e:
            self._process_field_error(e, k)

    def __getstate__(self):
        """
        For pickle serialization. This return the state of the model
        """
        return self.to_dict()

    def __setstate__(self, state):
        """
        For pickle serialization. This update the current model with the given state
        """
        self._update(state, ignore_missing=True)

    def validate(self):
        """
        Validate the entire model
        """

        for name, field in self._fields.items():
            try:
                field.validate(getattr(self, name))
            except InvalidModelFieldError as e:
                self._process_field_error(e, name)
            except InvalidModelError as e:
                e.model = self
                raise e

        if hasattr(self, "__validate__"):
            self.__validate__()

    def merge(self, other):
        if not isinstance(other, self.__class__):
            raise AztkError("Cannot merge {0} as is it not an instance of {1}".format(other, self.__class__.__name__))

        for field in other._fields.values():
            if field in other._data:
                field.merge(self, other._data[field])

        return self

    @classmethod
    def from_dict(cls, val: dict):
        return cls(**val)

    def to_dict(self):
        output = dict()
        for name, field in self._fields.items():
            output[name] = field.serialize(self)
        return output

    def __str__(self):
        return yaml.dump(self.to_dict(), default_flow_style=False)

    def _update(self, values, ignore_missing=False):
        for k, v in values.items():
            try:
                self[k] = v
            except AztkAttributeError as e:
                if not ignore_missing:
                    raise e

    def _process_field_error(self, e: InvalidModelFieldError, field: str):
        if not e.field:
            e.field = field

        if not e.model:
            e.model = self
        raise e
