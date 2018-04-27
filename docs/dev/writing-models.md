# Writing a model


## Getting started
In `aztk/models` create a new file with the name of your model `my_model.py`

In `aztk/models/__init__.py` add `from .my_model import MyModel`

Create a new class `MyModel` that inherit `ConfigurationBase`
```python
from aztk.internal import ConfigurationBase

class MyModel(ConfigurationBase):
    """
    MyModel is an sample model

    Args:
        input1 (str): This is the first input
    """
    def __init__(self, input1: str):
        self.input1 = input1

    def validate(self):
        pass

```

## Add validation

In `def validate` do any kind of checks and raise a `InvalidModelError` if there is any problems with the values

### Validate required
To validate required attributes call the parent `_validate_required` method. Method takes a list of attributes which should not be None

```python
def validate(self) -> bool:
    self._validate_required(["input1"])
```

### Custom validation
```python
    def validate(self) -> bool:
        if "foo" in self.input1:
            raise InvalidModelError("foo cannot be in input1")

```

## Convert dict to model

When inheriting from `ConfigurationBase` it comes with a `from_dict` class method which allows to convert a dict to this class
It works great for simple case where values are simple types(str, int, etc). If however you need to process it you can override the `_from_dict` method.

** Important: Do not override the `from_dict` method as this one will handle error and display them nicely **

```python
@classmethod
def _from_dict(cls, args: dict):
    if "input1" in args:
        args["input1"] = MyInput1Model.from_dict(args["input1"])

    return super()._from_dict(args)
```
