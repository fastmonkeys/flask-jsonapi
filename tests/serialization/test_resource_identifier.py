import pytest

from flask_jsonapi.errors import JSONAPIException
from flask_jsonapi.serialization import resource_identifier


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(1)


def test_dump(resource_registry, book):
    resource = resource_registry.by_type['books']
    assert resource_identifier.dump(resource=resource, model=book) == {
        'type': 'books',
        'id': '1'
    }


@pytest.mark.parametrize(
    'raw_data,error',
    [
        (
            [],
            '[] is not of type \'object\''
        ),
        (
            {'id': '1'},
            '"type" is a required property'
        ),
        (
            {'type': 'books'},
            '"id" is a required property'
        ),
        (
            {'type': 'books', 'id': 1},
            '1 is not of type \'string\''
        ),
        (
            {'type': 1, 'id': '1'},
            '1 is not of type \'string\''
        ),
        (
            {'type': 'books', 'id': 'asd'},
            '"asd" is not a valid int'
        ),
        (
            {'type': 'foo', 'id': '1'},
            '"foo" is not a valid type for this operation (expected "books")'
        ),
    ]
)
def test_load_invalid(resource_registry, raw_data, error):
    resource = resource_registry.by_type['books']
    with pytest.raises(JSONAPIException) as excinfo:
        resource_identifier.load(resource=resource, raw_data=raw_data)

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == error


def test_load_resource_not_found(resource_registry, fantasy_database):
    resource = resource_registry.by_type['books']
    with pytest.raises(JSONAPIException) as excinfo:
        resource_identifier.load(
            resource=resource,
            raw_data={'type': 'books', 'id': '123123'}
        )

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == (
        'The resource identified by ("books", "123123") type-id pair could '
        'not be found.'
    )


def test_load(resource_registry, fantasy_database, book):
    resource = resource_registry.by_type['books']
    model = resource_identifier.load(
        resource=resource,
        raw_data={'type': 'books', 'id': '1'}
    )
    assert model is book
