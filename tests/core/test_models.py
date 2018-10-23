from enum import Enum

import pytest
import yaml

from aztk.core.models import (ListMergeStrategy, Model, ModelMergeStrategy, fields)
from aztk.error import AztkAttributeError, InvalidModelFieldError

# pylint: disable=C1801


class UserState(Enum):
    Creating = "creating"
    Ready = "ready"
    Deleting = "deleting"


class UserInfo(Model):
    name = fields.String()
    age = fields.Integer()


class User(Model):
    info = fields.Model(UserInfo)
    enabled = fields.Boolean(default=True)
    state = fields.Enum(UserState, default=UserState.Ready)


def test_models():
    user = User(
        info=UserInfo(
            name="Highlander",
            age=800,
        ),
        enabled=False,
        state=UserState.Creating,
    )

    assert user.info.name == "Highlander"
    assert user.info.age == 800
    assert user.enabled is False
    assert user.state == UserState.Creating


def test_inherited_models():
    class ServiceUser(User):
        service = fields.String()

    user = ServiceUser(
        info=dict(
            name="Bob",
            age=59,
        ),
        enabled=False,
        service="bus",
    )
    user.validate()

    assert user.info.name == "Bob"
    assert user.info.age == 59
    assert user.enabled is False
    assert user.state == UserState.Ready
    assert user.service == "bus"


def test_raise_error_if_extra_parameters():
    class SimpleNameModel(Model):
        name = fields.String()

    with pytest.raises(AztkAttributeError, match="SimpleNameModel doesn't have an attribute called abc"):
        SimpleNameModel(name="foo", abc="123")


def test_enum_invalid_type_raise_error():
    class SimpleStateModel(Model):
        state = fields.Enum(UserState)

    with pytest.raises(
            InvalidModelFieldError,
            match=
            "SimpleStateModel state unknown is not a valid option. Use one of \\['creating', 'ready', 'deleting'\\]"):

        obj = SimpleStateModel(state="unknown")
        obj.validate()


def test_enum_parse_string():
    class SimpleStateModel(Model):
        state = fields.Enum(UserState)

    obj = SimpleStateModel(state="creating")
    obj.validate()

    assert obj.state == UserState.Creating


def test_convert_nested_dict_to_model():
    user = User(
        info=dict(
            name="Highlander",
            age=800,
        ),
        enabled=False,
        state="deleting",
    )
    assert isinstance(user.info, UserInfo)
    assert user.info.name == "Highlander"
    assert user.info.age == 800
    assert user.enabled is False
    assert user.state == UserState.Deleting


def test_raise_error_if_missing_required_field():
    class SimpleRequiredModel(Model):
        name = fields.String()

    missing = SimpleRequiredModel()

    with pytest.raises(InvalidModelFieldError, match="SimpleRequiredModel name is required"):
        missing.validate()


def test_raise_error_if_string_field_invalid_type():
    class SimpleStringModel(Model):
        name = fields.String()

    missing = SimpleStringModel(name=123)

    with pytest.raises(InvalidModelFieldError, match="SimpleStringModel name 123 should be a string"):
        missing.validate()


def test_raise_error_if_int_field_invalid_type():
    class SimpleIntegerModel(Model):
        age = fields.Integer()

    missing = SimpleIntegerModel(age='123')

    with pytest.raises(InvalidModelFieldError, match="SimpleIntegerModel age 123 should be an integer"):
        missing.validate()


def test_raise_error_if_bool_field_invalid_type():
    class SimpleBoolModel(Model):
        enabled = fields.Boolean()

    missing = SimpleBoolModel(enabled="false")

    with pytest.raises(InvalidModelFieldError, match="SimpleBoolModel enabled false should be a boolean"):
        missing.validate()


def test_merge_with_default_value():
    class SimpleMergeModel(Model):
        name = fields.String()
        enabled = fields.Boolean(default=True)

    record1 = SimpleMergeModel(enabled=False)
    assert record1.enabled is False

    record2 = SimpleMergeModel(name="foo")
    assert record2.enabled is True

    record1.merge(record2)
    assert record1.name == 'foo'
    assert record1.enabled is False


def test_merge_nested_model_merge_strategy():
    class ComplexModel(Model):
        model_id = fields.String()
        info = fields.Model(UserInfo, merge_strategy=ModelMergeStrategy.Merge)

    obj1 = ComplexModel(
        info=dict(
            name="John",
            age=29,
        ),
    )
    obj2 = ComplexModel(info=dict(age=38))

    assert obj1.info.age == 29
    assert obj2.info.age == 38

    obj1.merge(obj2)
    assert obj1.info.name == "John"
    assert obj1.info.age == 38


def test_merge_nested_model_override_strategy():
    class ComplexModel(Model):
        model_id = fields.String()
        info = fields.Model(UserInfo, merge_strategy=ModelMergeStrategy.Override)

    obj1 = ComplexModel(
        info=dict(
            name="John",
            age=29,
        ),
    )
    obj2 = ComplexModel(info=dict(age=38))

    assert obj1.info.age == 29
    assert obj2.info.age == 38

    obj1.merge(obj2)
    assert obj1.info.name is None
    assert obj1.info.age == 38


def test_list_field_convert_model_correctly():
    class UserList(Model):
        infos = fields.List(UserInfo)

    obj = UserList(
        infos=[
            dict(
                name="John",
                age=29,
            ),
        ],
    )
    obj.validate()

    assert len(obj.infos) == 1
    assert isinstance(obj.infos[0], UserInfo)
    assert obj.infos[0].name == "John"
    assert obj.infos[0].age == 29


def test_list_field_is_never_required():
    class UserList(Model):
        infos = fields.List(UserInfo)

    obj = UserList()
    obj.validate()

    assert isinstance(obj.infos, (list,))
    assert len(obj.infos) == 0

    infos = obj.infos
    infos.append(UserInfo())
    assert len(obj.infos) == 1

    obj2 = UserList(infos=None)
    assert isinstance(obj2.infos, (list,))
    assert len(obj2.infos) == 0


def test_list_field_ignore_none_entries():
    class UserList(Model):
        infos = fields.List(UserInfo)

    obj = UserList(infos=[None, None])
    obj.validate()

    assert isinstance(obj.infos, (list,))
    assert len(obj.infos) == 0


def test_merge_nested_model_append_strategy():
    class UserList(Model):
        infos = fields.List(UserInfo, merge_strategy=ListMergeStrategy.Append)

    obj1 = UserList(
        infos=[
            dict(
                name="John",
                age=29,
            ),
        ],
    )

    obj2 = UserList(
        infos=[
            dict(
                name="Frank",
                age=38,
            ),
        ],
    )

    assert len(obj1.infos) == 1
    assert len(obj2.infos) == 1
    assert obj1.infos[0].name == "John"
    assert obj1.infos[0].age == 29
    assert obj2.infos[0].name == "Frank"
    assert obj2.infos[0].age == 38

    obj1.merge(obj2)
    assert len(obj1.infos) == 2
    assert obj1.infos[0].name == "John"
    assert obj1.infos[0].age == 29
    assert obj1.infos[1].name == "Frank"
    assert obj1.infos[1].age == 38


def test_serialize_simple_model_to_yaml():
    info = UserInfo(name="John", age=29)
    output = yaml.dump(info)

    assert output == "!!python/object:tests.core.test_models.UserInfo {age: 29, name: John}\n"

    info_parsed = yaml.load(output)

    assert isinstance(info_parsed, UserInfo)
    assert info_parsed.name == "John"
    assert info_parsed.age == 29


def test_serialize_nested_model_to_yaml():
    user = User(
        info=dict(name="John", age=29),
        enabled=True,
        state=UserState.Deleting,
    )
    output = yaml.dump(user)

    assert output == "!!python/object:tests.core.test_models.User\nenabled: true\ninfo: {age: 29, name: John}\nstate: deleting\n"

    user_parsed = yaml.load(output)

    assert isinstance(user_parsed, User)
    assert isinstance(user_parsed.info, UserInfo)
    assert user_parsed.info.name == "John"
    assert user_parsed.info.age == 29
    assert user_parsed.state == UserState.Deleting
    assert user_parsed.enabled is True
