import collections

from aztk.error import InvalidModelFieldError


class Validator:
    """
    Base class for a validator.
    To write your validator extend this class and implement the validate method.
    To raise an error raise  InvalidModelFieldError
    """

    def __call__(self, value):
        self.validate(value)

    def validate(self, value):
        raise NotImplementedError()


class Required(Validator):
    """
    Validate the field value is not `None`
    """

    def validate(self, value):
        if value is None:
            raise InvalidModelFieldError("is required")


class String(Validator):
    """
    Validate the value of the field is a `str`
    """

    def validate(self, value):
        if not value:
            return

        if not isinstance(value, str):
            raise InvalidModelFieldError("{0} should be a string".format(value))


class Integer(Validator):
    """
    Validate the value of the field is a `int`
    """

    def validate(self, value):
        if not value:
            return

        if not isinstance(value, int):
            raise InvalidModelFieldError("{0} should be an integer".format(value))


class Float(Validator):
    """
    Validate the value of the field is a `float`
    """

    def validate(self, value):
        if not value:
            return

        if not isinstance(value, float):
            raise InvalidModelFieldError("{0} should be a float".format(value))


class Boolean(Validator):
    """This validator forces fields values to be an instance of `bool`."""

    def validate(self, value):
        if not value:
            return

        if not isinstance(value, bool):
            raise InvalidModelFieldError("{0} should be a boolean".format(value))


class In(Validator):
    """
    Validate the field value is in the list of allowed choices
    """

    def __init__(self, choices):
        self.choices = choices

    def validate(self, value):
        if not value:
            return

        if value not in self.choices:
            raise InvalidModelFieldError("{0} should be in {1}".format(value, self.choices))


class InstanceOf(Validator):
    """
    Check if the field is an instance of the given type
    """

    def __init__(self, cls):
        self.type = cls

    def validate(self, value):
        if not value:
            return

        if not isinstance(value, self.type):
            raise InvalidModelFieldError("should be an instance of '{}'".format(self.type.__name__))


class Model(Validator):
    """
    Validate the field is a model
    """

    def __init__(self, model):
        self.model = model

    def validate(self, value):
        if not value:
            return

        if not isinstance(value, self.model):
            raise InvalidModelFieldError("should be an instance of '{}'".format(self.model.__name__))

        value.validate()


class List(Validator):
    """
    Validate the given item is a list
    """

    def __init__(self, *validators):
        self.validators = validators

    def validate(self, value):
        if not value:
            return

        if not isinstance(value, collections.MutableSequence):
            raise InvalidModelFieldError("should be a list")

        for i in value:
            for validator in self.validators:
                validator(i)
