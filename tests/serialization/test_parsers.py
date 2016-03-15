import pytest

from flask_jsonapi.errors import JSONAPIException
from flask_jsonapi.serialization import _parsers


def test_object_invalid_type():
    parser = _parsers.Object()
    with pytest.raises(JSONAPIException) as excinfo:
        parser('foo')

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == '"foo" is not of type \'object\''
    assert errors[0].source_pointer == ''


def test_object_invalid_properties():
    parser = _parsers.Object(properties={
        'id': _parsers.String(),
        'type': _parsers.String()
    })

    with pytest.raises(JSONAPIException) as excinfo:
        parser({'id': 123, 'type': []})

    errors = excinfo.value.errors
    assert len(errors) == 2
    assert errors[0].detail == '123 is not of type \'string\''
    assert errors[0].source_pointer == '/id'
    assert errors[1].detail == '[] is not of type \'string\''
    assert errors[1].source_pointer == '/type'


def test_object_one_additional_property():
    parser = _parsers.Object(additional_properties=False)
    with pytest.raises(JSONAPIException) as excinfo:
        parser({'foo': 1})

    errors = excinfo.value.errors
    assert len(errors) == 1

    assert errors[0].detail == (
        'Additional properties are not allowed ("foo" was unexpected)'
    )
    assert errors[0].source_pointer == ''


def test_object_many_additional_properties():
    parser = _parsers.Object(additional_properties=False)
    with pytest.raises(JSONAPIException) as excinfo:
        parser({'foo': 1, 'bar': 2})

    errors = excinfo.value.errors
    assert len(errors) == 1

    assert errors[0].detail == (
        'Additional properties are not allowed ("bar", "foo" were unexpected)'
    )
    assert errors[0].source_pointer == ''


def test_object_missing_required_properties():
    parser = _parsers.Object(
        properties={
            'type': _parsers.String(),
            'id': _parsers.String(),
        },
        required=['id', 'type']
    )
    with pytest.raises(JSONAPIException) as excinfo:
        parser({'type': 'books'})

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == '"id" is a required property'
    assert errors[0].source_pointer == ''


def test_object_valid():
    parser = _parsers.Object(
        properties={
            'id': _parsers.String(),
            'type': _parsers.String()
        },
        additional_properties=True
    )
    data = parser({'type': 'books', 'id': '1', 'meta': {}})
    assert data == {'type': 'books', 'id': '1', 'meta': {}}


def test_array_invalid_type():
    parser = _parsers.Array(_parsers.String())
    with pytest.raises(JSONAPIException) as excinfo:
        parser('foo')

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == '"foo" is not of type \'array\''
    assert errors[0].source_pointer == ''


def test_array_invalid_item():
    parser = _parsers.Array(_parsers.String())
    with pytest.raises(JSONAPIException) as excinfo:
        parser(['foo', 123])

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == "123 is not of type 'string'"
    assert errors[0].source_pointer == '/1'


def test_array_nested_errors():
    parser = _parsers.Array(_parsers.Array(_parsers.String()))
    with pytest.raises(JSONAPIException) as excinfo:
        parser([['foo', 123], 'bar'])

    errors = excinfo.value.errors
    assert len(errors) == 2
    assert errors[0].detail == "123 is not of type 'string'"
    assert errors[0].source_pointer == "/0/1"
    assert errors[1].detail == '"bar" is not of type \'array\''
    assert errors[1].source_pointer == "/1"


def test_array_valid():
    parser = _parsers.Array(_parsers.String())
    data = parser(['foo', 'bar'])
    assert data == ['foo', 'bar']


def test_string_invalid():
    parser = _parsers.String()
    with pytest.raises(JSONAPIException) as excinfo:
        parser({})

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == "{} is not of type 'string'"
    assert errors[0].source_pointer == ''


def test_string_valid():
    parser = _parsers.String()
    assert parser(u'valid') == u'valid'
