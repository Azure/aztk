import collections
import enum

from aztk.error import InvalidModelFieldError

from . import validators as aztk_validators


class ModelMergeStrategy(enum.Enum):
    Override = 1
    """
    Override the value with the other value
    """
    Merge = 2
    """
    Try to merge value nested
    """


class ListMergeStrategy(enum.Enum):
    Replace = 1
    """
    Override the value with the other value
    """
    Append = 2
    """
    Append all the values of the new list
    """


# pylint: disable=W0212
class Field:
    """
    Base class for all model fields
    """

    def __init__(self, *validators, **kwargs):
        self.default = kwargs.get("default")
        self.required = "default" not in kwargs
        self.validators = []

        if self.required:
            self.validators.append(aztk_validators.Required())

        self.validators.extend(validators)

        choices = kwargs.get("choices")
        if choices:
            self.validators.append(aztk_validators.In(choices))

    def validate(self, value):
        for validator in self.validators:
            validator(value)

    def __get__(self, instance, owner):
        if instance is not None:
            value = instance._data.get(self)
            if value is None:
                return instance._defaults.setdefault(self, self._default(instance))
            return value

        return self

    def __set__(self, instance, value):
        instance._data[self] = value

    def merge(self, instance, value):
        """
        Method called when merging 2 models together.
        This is overridden in some of the fields where merge can be handled differently
        """
        if value is not None:
            instance._data[self] = value

    def serialize(self, instance):
        return self.__get__(instance, None)

    def _default(self, model):
        if callable(self.default):
            return self.__call_default(model)

        return self.default

    def __call_default(self, *args):
        try:
            return self.default()
        except TypeError as error:
            try:
                return self.default(*args)
            except TypeError:
                raise error


class String(Field):
    """
    Model String field
    """

    def __init__(self, *args, **kwargs):
        super().__init__(aztk_validators.String(), *args, **kwargs)


class Integer(Field):
    """
    Model Integer field
    """

    def __init__(self, *args, **kwargs):
        super().__init__(aztk_validators.Integer(), *args, **kwargs)


class Float(Field):
    """
    Model Float field
    """

    def __init__(self, *args, **kwargs):
        super().__init__(aztk_validators.Float(), *args, **kwargs)


class Boolean(Field):
    """
    Model Boolean field
    """

    def __init__(self, *args, **kwargs):
        super().__init__(aztk_validators.Boolean(), *args, **kwargs)


class List(Field):
    """
    Field that should be a list
    """

    def __init__(self, model=None, **kwargs):
        self.model = model
        kwargs.setdefault("default", list)
        self.merge_strategy = kwargs.get("merge_strategy", ListMergeStrategy.Append)
        self.skip_none = kwargs.get("skip_none", True)

        super().__init__(aztk_validators.List(*kwargs.get("inner_validators", [])), **kwargs)

    def __set__(self, instance, value):
        if isinstance(value, collections.MutableSequence):
            value = self._resolve(value)
        if value is None:
            value = []
        super().__set__(instance, value)

    def _resolve(self, value):
        result = []
        for item in value:
            if item is None and self.skip_none:    # Skip none values
                continue

            if self.model and isinstance(item, collections.MutableMapping):
                item = self.model(**item)
            result.append(item)
        return result

    def merge(self, instance, value):
        if value is None:
            value = []

        if self.merge_strategy == ListMergeStrategy.Append:
            current = instance._data.get(self)
            if current is None:
                current = []
            value = current + value

        instance._data[self] = value

    def serialize(self, instance):
        items = super().serialize(instance)
        output = []
        if items is not None:
            for item in items:
                if hasattr(item, "to_dict"):
                    output.append(item.to_dict())
                else:
                    output.append(item)
        return output


class Model(Field):
    """
    Field is another model

    Args:
        model (aztk.core.models.Model): Model object that field should be
        merge_strategy (ModelMergeStrategy): When merging models how should the nested model be merged.
            Default: `ModelMergeStrategy.merge`
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(aztk_validators.Model(model), *args, **kwargs)

        self.model = model
        self.merge_strategy = kwargs.get("merge_strategy", ModelMergeStrategy.Merge)

    def __set__(self, instance, value):
        if isinstance(value, collections.MutableMapping):
            value = self.model(**value)

        super().__set__(instance, value)

    def merge(self, instance, value):
        if self.merge_strategy == ModelMergeStrategy.Merge:
            current = instance._data.get(self)
            if current is not None:
                current.merge(value)
                value = current

        instance._data[self] = value

    def serialize(self, instance):
        val = super().serialize(instance)
        if val is not None:
            return val.to_dict()
        else:
            return None


class Enum(Field):
    """
    Field that should be an enum
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(aztk_validators.InstanceOf(model), *args, **kwargs)

        self.model = model

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.model):
            try:
                value = self.model(value)
            except ValueError:
                available = [e.value for e in self.model]
                raise InvalidModelFieldError("{0} is not a valid option. Use one of {1}".format(value, available))
        super().__set__(instance, value)

    def serialize(self, instance):
        val = super().serialize(instance)
        if val is not None:
            return val.value
        else:
            return None
