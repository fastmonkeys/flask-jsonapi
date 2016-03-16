import pytest

from flask_jsonapi.errors import JSONAPIException
from flask_jsonapi.serialization import resource_object


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(1)


@pytest.mark.parametrize('fields,output', [
    (set(), {
        'type': 'books',
        'id': '1',
        'links': {
            'self': 'http://example.com/books/1'
        }
    }),
    ({'title', 'author', 'stores'}, {
        'type': 'books',
        'id': '1',
        'attributes': {
            'title': 'The Fellowship of the Ring'
        },
        'relationships': {
            'author': {
                'data': {'type': 'authors', 'id': '1'},
                'links': {
                    'self': 'http://example.com/books/1/relationships/author',
                    'related': 'http://example.com/books/1/author'
                }
            },
            'stores': {
                'links': {
                    'self': 'http://example.com/books/1/relationships/stores',
                    'related': 'http://example.com/books/1/stores'
                }
            }
        },
        'links': {
            'self': 'http://example.com/books/1'
        }
    }),
])
def test_dump(resource_registry, book, fields, output):
    resource = resource_registry.by_type['books']
    assert resource_object.dump(
        resource=resource,
        model=book,
        fields=fields
    ) == output


@pytest.mark.parametrize(
    'raw_data,error',
    [
        ([], '[] is not of type \'object\''),
        ({}, '"type" is a required property'),
        (
            {'type': 'foo'},
            '"foo" is not a valid type for this operation (expected "books")'
        ),
    ]
)
def test_load_invalid(resource_registry, raw_data, error):
    resource = resource_registry.by_type['books']
    with pytest.raises(JSONAPIException) as excinfo:
        resource_object.load(resource=resource, raw_data=raw_data)

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == error
