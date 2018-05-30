# Writing a model


## Getting started
In `aztk/models` create a new file with the name of your model `my_model.py`

In `aztk/models/__init__.py` add `from .my_model import MyModel`

Create a new class `MyModel` that inherit `Modle`
```python
from aztk.core.models import Model, fields

class MyModel(Model):
    """
    MyModel is an sample model

    Args:
        input1 (str): This is the first input
    """

    input1 = fields.String()

    def __validate__(self):
        pass

```

### Available fields types

Check `aztk/core/models/fields.py` for the sources

* `Field`: Base field class
* `String`: Field that validate it is given a string
* `Integer`: Field that validate it is given a int
* `Float`: Field that validate it is given a float
* `Boolean`: Field that validate it is given a boolean
* `List`: Field that validate it is given a list and can also automatically convert entries to the given model type.
* `Model`: Field that map to another model. If passed a dict it will automatically try to convert to the Model type
* `Enum`: Field which value should be an enum. It will convert automatically to the enum if given the value.

## Add validation
The fields provide basic validation automatically. A field without a default will be marked as required.

To provide model wide validation implement a `__validate__` method  and raise a `InvalidModelError` if there is any problems with the values

```python
def __validate__(self):
    if 'secret' in self.input1:
        raise InvalidModelError("Input1 contains secrets")

```

## Convert dict to model

When inheriting from `Model` it comes with a `from_dict` class method which allows to convert a dict to this class
